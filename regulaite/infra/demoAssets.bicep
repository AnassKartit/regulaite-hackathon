@description('Creates intentionally non-compliant Cognitive Services accounts for demo')
param location string = resourceGroup().location
param demoTag  string = 'demo'
var   suffix   = uniqueString(resourceGroup().id)

resource badFace 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: 'citycctv${suffix}'
  location: location
  kind: 'CognitiveServices'
  sku:   { name: 'S0' }
  tags: {
    purpose: 'face tracking'
    demo:    demoTag
  }
}

resource loanAi 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: 'loanai${suffix}'
  location: location
  kind: 'OpenAI'
  sku: { name: 'S0' }
  tags: {
    sector: 'credit'
    demo:   demoTag
  }
}

resource prodTracker 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: 'prodtracker${suffix}'
  location: location
  kind: 'CognitiveServices'
  sku: { name: 'S0' }
  tags: {
    purpose: 'employee_monitoring'
    demo:    demoTag
  }
}

output assetNames array = [
  badFace.name
  loanAi.name
  prodTracker.name
]
