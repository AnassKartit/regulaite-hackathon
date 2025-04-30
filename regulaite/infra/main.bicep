// ============================================================================
//  regulaite – hackathon infra (OpenAI + Search + Storage + Functions)
//  API versions: 2024-10-01 for AI Service + deployments
// ============================================================================

// ───────── PARAMETERS (edit only if you really need to) ───────────
param location  string = resourceGroup().location
param baseName  string = 'regulaite'      // used as prefix everywhere
@allowed([ true, false ])
param deployDemoAssets bool = false      // flag to control demo assets deployment

// fixed suffix (keeps names stable but unique enough for the hack)
var suffix       = 'hackathon'

// model deployment names & versions (override with --parameters if you like)
var chatDeploymentName  = 'gpt-4.1'
var chatModelName       = 'gpt-4.1'
var chatModelVersion    = '2025-04-14'   // Azure catalogue tag

var embedDeploymentName = 'text-embedding-3-large'
var embedModelName      = 'text-embedding-3-large'
var embedModelVersion   = '1'

// ───────── 1️⃣  AZURE AI SERVICE ACCOUNT (+2 deployments) ─────────
resource oai 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name:     '${baseName}-oai-${suffix}'
  location: location
  kind:     'AIServices'
  sku:      { name: 'S0' }                // pay-go tier
  identity: { type: 'SystemAssigned' }
  properties: {
    customSubDomainName: '${baseName}-oai-${suffix}'
    publicNetworkAccess: 'Enabled'
    networkAcls: { defaultAction: 'Allow' }
    encryption:   { keySource: 'Microsoft.CognitiveServices' }
  }
}

// GPT-4.1 deployment
resource gpt4Deploy 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' = {
  parent: oai
  name:   chatDeploymentName
  sku: {
    name: 'GlobalStandard'
    capacity: 100    // adjust down if you hit quota
  }
  properties: {
    model: {
      format:  'OpenAI'
      name:    chatModelName
      version: chatModelVersion
    }
  }
}

// text-embedding-3-large deployment
resource embedDeploy 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' = {
  parent: oai
  name:   embedDeploymentName
  dependsOn: [
    gpt4Deploy
  ]
  sku: {
    name: 'GlobalStandard'
    capacity: 10
  }
  properties: {
    model: {
      format:  'OpenAI'
      name:    embedModelName
      version: embedModelVersion
    }
  }
}

// ───────── 2️⃣  AZURE AI SEARCH  (basic – avoids free-tier limit) ─
resource search 'Microsoft.Search/searchServices@2023-11-01' = {
  name:     '${baseName}-search-${suffix}'
  location: location
  sku:      { name: 'basic' }             // 3-unit quota per sub
  properties: {
    replicaCount: 1
    partitionCount: 1
  }
}

// ───────── 3️⃣  STORAGE + FUNCTIONS  ──────────────────────────────
var shortSuffix = toLower(substring(uniqueString(resourceGroup().id), 0, 6))

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name:     '${baseName}st${shortSuffix}'   // 16 chars ⇒ valid
  location: location
  sku:      { name: 'Standard_LRS' }
  kind:     'StorageV2'
}

resource plan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name:     '${baseName}-plan-${suffix}'
  location: location
  sku:      { name: 'Y1', tier: 'Dynamic' }   // Consumption
}

resource func 'Microsoft.Web/sites@2023-01-01' = {
  name:     '${baseName}-api-${suffix}'
  location: location
  kind:     'functionapp'
  properties: {
    serverFarmId: plan.id
    siteConfig: {
      // NOTE: each element **must** be an object with `name` and `value`
      appSettings: [
        // mandatory Functions setting
        {
          name: 'AzureWebJobsStorage'
          value: concat(
              'DefaultEndpointsProtocol=https;AccountName=',storage.name,
              ';AccountKey=',listKeys(storage.id, '2023-05-01').keys[0].value,
              ';EndpointSuffix=core.windows.net')
        }
        { name: 'AZURE_OPENAI_ENDPOINT', value: concat('https://',oai.name,'.openai.azure.com/') }
        { name: 'AZURE_OPENAI_KEY',      value: listKeys(oai.id, '2023-05-01').key1 }
        { name: 'AZURE_OPENAI_MODEL',    value: chatDeploymentName }
        { name: 'AZURE_EMBED_MODEL',     value: embedDeploymentName }
        { name: 'AZURE_SEARCH_ENDPOINT', value: concat('https://',search.name,'.search.windows.net') }
        { name: 'AZURE_SEARCH_KEY',      value: listAdminKeys(search.id, '2023-11-01').primaryKey }
        { name: 'AZURE_SEARCH_INDEX',    value: 'regulaite-laws' }
        { name: 'STORAGE_ACC',           value: storage.name }
      ]
    }
  }
}

// ───────── 4️⃣  DEMO ASSETS (optional) ─────────────────────────────
module demoAssets './demoAssets.bicep' = if (deployDemoAssets) {
  name: 'demoAssets'
  params: {
    location: location
    demoTag: 'demo'
  }
}

// ───────── OUTPUTS (no secrets!) ──────────────────────────────────
output openaiEndpoint   string = 'https://${oai.name}.openai.azure.com/'
output chatDeployment   string = chatDeploymentName
output embedDeployment  string = embedDeploymentName
output AZURE_SEARCH_ENDPOINT   string = 'https://${search.name}.search.windows.net'
output functionBaseUrl  string = 'https://${func.name}.azurewebsites.net'
output AZURE_OPENAI_ENDPOINT string = 'https://${oai.name}.openai.azure.com/'
output AZURE_OPENAI_KEY      string = listKeys(oai.id, '2023-05-01').key1
output AZURE_OPENAI_MODEL    string = chatDeploymentName
output AZURE_EMBED_MODEL     string = embedDeploymentName
output AZURE_SEARCH_KEY      string = listAdminKeys(search.id, '2023-11-01').primaryKey
output AZURE_SEARCH_INDEX    string = 'regulaite-laws'
output STORAGE_ACC           string = storage.name
output STORAGE_KEY           string = listKeys(storage.id, '2023-05-01').keys[0].value
output demoMode             string = deployDemoAssets ? '✅ Demo assets will be deployed' : '❌ Demo assets disabled'
output demoAssetNames     array  = deployDemoAssets ? demoAssets.outputs.assetNames : []
