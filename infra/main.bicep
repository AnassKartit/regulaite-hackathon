param location  string = resourceGroup().location
param baseName  string = 'regulaite'
@allowed([ true, false ])
param deployDemoAssets bool = false

var suffix       = 'hackathon'

var chatDeploymentName  = 'gpt-4.1'
var chatModelName       = 'gpt-4.1'
var chatModelVersion    = '2025-04-14'

var embedDeploymentName = 'text-embedding-3-large'
var embedModelName      = 'text-embedding-3-large'
var embedModelVersion   = '1'
resource oai 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name:     '${baseName}-oai-${suffix}'
  location: location
  kind:     'AIServices'
  sku:      { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    customSubDomainName: '${baseName}-oai-${suffix}'
    publicNetworkAccess: 'Enabled'
    networkAcls: { defaultAction: 'Allow' }
    encryption:   { keySource: 'Microsoft.CognitiveServices' }
  }
}
resource gpt4Deploy 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' = {
  parent: oai
  name:   chatDeploymentName
  sku: {
    name: 'GlobalStandard'
    capacity: 100
  }
  properties: {
    model: {
      format:  'OpenAI'
      name:    chatModelName
      version: chatModelVersion
    }
  }
}
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
resource search 'Microsoft.Search/searchServices@2023-11-01' = {
  name:     '${baseName}-search-${suffix}'
  location: location
  sku:      { name: 'basic' }
  properties: {
    replicaCount: 1
    partitionCount: 1
  }
}
var shortSuffix = toLower(substring(uniqueString(resourceGroup().id), 0, 6))

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name:     '${baseName}st${shortSuffix}'
  location: location
  sku:      { name: 'Standard_LRS' }
  kind:     'StorageV2'
}

resource plan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name:     '${baseName}-plan-${suffix}'
  location: location
  sku:      { name: 'Y1', tier: 'Dynamic' }
}

resource func 'Microsoft.Web/sites@2023-01-01' = {
  name:     '${baseName}-api-${suffix}'
  location: location
  kind:     'functionapp'
  properties: {
    serverFarmId: plan.id
    siteConfig: {
      appSettings: [
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


resource swa 'Microsoft.Web/staticSites@2023-10-01' = {
  name:  '${baseName}-web-${suffix}'
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }

  properties: {
    repositoryUrl: 'https://github.com/${baseName}/${baseName}'
    branch:        'main'
    buildProperties: {
      appLocation:              'src/web'
      apiLocation:              ''
      appArtifactLocation:      'dist'
      skipGithubActionWorkflowGeneration: true
    }
    allowConfigFileUpdates: true
  }
}

resource funcCors 'Microsoft.Web/sites/config@2023-01-01' = {
  name: '${func.name}/web'
  properties: {
    cors: {
      allowedOrigins: [
        swa.properties.defaultHostname
      ]
    }
  }
  dependsOn: [
    swa
  ]
}


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
output staticWebUrl          string = 'https://${swa.properties.defaultHostname}'
output demoMode             string = deployDemoAssets ? '✅ Demo assets will be deployed' : '❌ Demo assets disabled'
