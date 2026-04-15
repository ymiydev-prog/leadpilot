export async function onRequest({ request, next }) {
  const url = new URL(request.url);

  if (url.pathname.startsWith('/api/')) {
    const insforgeUrl = `https://nv96hw8d.functions.insforge.app${url.pathname}`;

    const headers = new Headers();
    headers.set('Content-Type', 'application/json');

    if (request.headers.has('Authorization')) {
      headers.set('Authorization', request.headers.get('Authorization'));
    }

    const fetchOptions = {
      method: request.method,
      headers: headers,
    };

    if (request.method !== 'GET' && request.method !== 'HEAD') {
      const body = await request.text();
      fetchOptions.body = body;
    }

    const response = await fetch(insforgeUrl, fetchOptions);
    const text = await response.text();

    return new Response(text, {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    });
  }

  return next(request);
}
