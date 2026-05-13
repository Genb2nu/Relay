# SimplifyNext Model-Driven App Patterns

## Purpose

Standard MDA patterns that Forge-MDA must follow. All MDA components are
built via the Dataverse API — never manually in the Power Apps studio.

---

## App Module Creation

### Create App Module

```http
POST /api/data/v9.2/appmodules
Content-Type: application/json

{
  "name": "{AppDisplayName}",
  "uniquename": "{prefix}_{AppUniqueName}",
  "webresourceid@odata.bind": "/webresources({iconWebResourceId})",
  "clienttype": 4,
  "appmoduleversion": "1.0.0.0",
  "isdefault": false,
  "description": "{Description}"
}
```

`clienttype`: 4 = Unified Interface (always use this)

### Get Existing App Module

```http
GET /api/data/v9.2/appmodules?$filter=uniquename eq '{prefix}_{AppUniqueName}'&$select=appmoduleid,uniquename
```

---

## Sitemap XML Pattern

The sitemap defines the navigation structure of the MDA. Always deploy via API.

### Standard Sitemap XML

```xml
<SiteMap>
  <Area Id="Area_{EntityGroup}" Title="{Area Display Name}" Icon="Flags/32x32/outline_checkmark_blue.svg" DescriptionResourceId="{prefix}_Area_{EntityGroup}">
    <Group Id="Group_{EntityGroup}_Main" Title="{Group Name}">
      <SubArea Id="SubArea_{prefix}_{entity}" Entity="{prefix}_{entity}" Title="{Entity Display Name}" Icon="/_imgs/ico_16_dynamicpropertyinstance.png"/>
    </Group>
    <Group Id="Group_{EntityGroup}_Admin" Title="Administration" AvailableForPhones="false">
      <SubArea Id="SubArea_{prefix}_admin" Title="Settings" Url="/main.aspx?pagetype=entitylist&amp;etn={prefix}_{entity}"/>
    </Group>
  </Area>
</SiteMap>
```

### Patch Sitemap

```http
GET /api/data/v9.2/sitemaps?$filter=sitemapid ne null&$select=sitemapid,sitemapxml
→ get sitemapid

PATCH /api/data/v9.2/sitemaps({sitemapId})
Content-Type: application/json

{ "sitemapxml": "{escaped sitemap XML}" }
```

After patching, always publish:
```http
POST /api/data/v9.2/PublishXml
{ "ParameterXml": "<importexportxml><sitemaps><sitemap>{sitemapId}</sitemap></sitemaps></importexportxml>" }
```

---

## Form XML Pattern

### Get Existing Form

```http
GET /api/data/v9.2/systemforms?$filter=objecttypecode eq '{prefix}_{entity}' and type eq 2&$select=formid,name,formxml
```

Form types: 1=Dashboard, 2=Main, 3=Mobile Express, 4=Quick View, 5=Quick Create, 11=Card

### Patch Form XML

```http
PATCH /api/data/v9.2/systemforms({formId})
Content-Type: application/json

{ "formxml": "{escaped form XML}" }
```

### Standard Main Form XML

```xml
<form>
  <tabs>
    <tab name="tab_general" id="{tab-guid}" IsUserDefined="0" locklevel="0" showlabel="true" expanded="true">
      <labels>
        <label description="General" languagecode="1033"/>
      </labels>
      <columns>
        <column width="100%">
          <sections>
            <section name="section_info" showlabel="false" showbar="false" locklevel="0" id="{section-guid}" IsUserDefined="0" layout="varwidth" columns="111" labelwidth="115" celllabelalignment="Left" celllabelposition="Left">
              <labels>
                <label description="General Information" languagecode="1033"/>
              </labels>
              <rows>
                <row>
                  <cell id="{cell-guid}" showlabel="true" locklevel="0">
                    <labels>
                      <label description="{Column Label}" languagecode="1033"/>
                    </labels>
                    <control id="{prefix}_{columnname}" classid="{control-classid}" datafieldname="{prefix}_{columnname}" disabled="false"/>
                  </cell>
                </row>
              </rows>
            </section>
          </sections>
        </column>
      </columns>
    </tab>
  </tabs>
  <formparameters/>
  <controlDescriptions/>
</form>
```

Control classids:
- Text: `{4273EDBD-AC1D-40d3-9FB2-095C621B552D}`
- Lookup: `{270BD3DB-D9AF-4782-9025-509E298DEC0A}`
- Choice: `{3EF39988-22BB-4f0b-BBBE-64B5A3748AEE}`
- DateTime: `{5B773807-9FB2-42db-97C3-7A91EFF8ADFF}`
- Checkbox: `{B0C6723A-8503-4fd7-BB28-C8A06AC933C2}`

---

## View Configuration

### Get Existing Views

```http
GET /api/data/v9.2/savedqueries?$filter=returnedtypecode eq '{prefix}_{entity}' and querytype eq 0&$select=savedqueryid,name,fetchxml,layoutxml
```

### Create or Update View

```http
POST /api/data/v9.2/savedqueries
Content-Type: application/json

{
  "name": "{View Name}",
  "returnedtypecode": "{prefix}_{entity}",
  "querytype": 0,
  "isdefault": false,
  "fetchxml": "{escaped fetchxml}",
  "layoutxml": "{escaped layoutxml}"
}
```

### Standard FetchXML

```xml
<fetch version="1.0" output-format="xml-platform" mapping="logical" distinct="false">
  <entity name="{prefix}_{entity}">
    <attribute name="{prefix}_{primarycolumn}"/>
    <attribute name="statuscode"/>
    <attribute name="createdon"/>
    <order attribute="{prefix}_{primarycolumn}" descending="false"/>
    <filter type="and">
      <condition attribute="statecode" operator="eq" value="0"/>
    </filter>
  </entity>
</fetch>
```

---

## Publish After All MDA Changes

After all sitemap, form, and view changes:

```http
POST /api/data/v9.2/PublishAllXml
```

Always publish before Sentinel verification.

---

## Add Entity to App Module

```http
POST /api/data/v9.2/appmodules({appModuleId})/appmodule_metadata/$ref
Content-Type: application/json

{ "@odata.id": "{baseUrl}/api/data/v9.2/EntityDefinitions(LogicalName='{prefix}_{entity}')" }
```
