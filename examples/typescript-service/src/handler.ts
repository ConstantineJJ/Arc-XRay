import {readItems} from './storage';

export async function handle(_request: unknown, response: {json: (items: unknown) => void}) {
  const items = await readItems();
  response.json(items);
}
