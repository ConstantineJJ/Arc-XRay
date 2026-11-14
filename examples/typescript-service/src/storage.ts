import {readFile} from 'node:fs/promises';

export async function readItems() {
  return JSON.parse(await readFile('items.json', 'utf8'));
}
