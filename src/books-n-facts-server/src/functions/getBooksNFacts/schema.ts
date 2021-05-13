export default {
  type: "object",
  properties: {
    query: { type: 'string' },
    count: { type: 'integer', default: 5, minimum: 1, maximum: 10 }
  },
  required: ['query']
} as const;
