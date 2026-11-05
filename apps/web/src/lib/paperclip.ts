import { Client } from 'paperclip';

const client = new Client({
  apiKey: process.env.PAPERCLIP_API_KEY,
  baseUrl: process.env.PAPERCLIP_API_URL || 'https://api.paperclip.ai/v1',
});

export default client;
