import Ajv from 'ajv';

const ajv = new Ajv();

const scanResponseSchema = {
  type: 'object',
  properties: {
    reports: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          score: { type: 'number' },
          details: { type: 'string' }
        },
        required: ['name', 'score', 'details']
      }
    },
    pdf: { type: 'string' }
  },
  required: ['reports', 'pdf']
};

const validateScanResponse = ajv.compile(scanResponseSchema);

export function validateResponse(data) {
  if (!validateScanResponse(data)) {
    console.error('Response data does not match schema:', validateScanResponse.errors);
    return false;
  }
  return true;
}