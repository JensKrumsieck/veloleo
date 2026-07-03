import { readFile } from 'fs/promises';
import path from 'path';

export async function GET({ params }) {
    const filePath = path.join('../data', params.filename);
    const file = await readFile(filePath);
    return new Response(file, {
        headers: { 'Content-Type': 'image/png' }
    });
}