import { NextRequest, NextResponse } from "next/server";

// Force dynamic: empêche Next.js d'optimiser statiquement ces routes
// (sinon le body de la requête peut être vide côté serveur)
export const dynamic = "force-dynamic";

function backendBase(): string {
  return (process.env.API_URL || "http://127.0.0.1:8001").replace(/\/$/, "");
}

async function forward(request: NextRequest, segments: string[]): Promise<NextResponse> {
  const path = segments.join("/");
  const u = new URL(request.url);
  const target = `${backendBase()}/api/v1/${path}${u.search}`;

  // Copie les headers nécessaires (autorisation + type de contenu avec boundary pour multipart)
  const headers = new Headers();
  for (const name of ["authorization", "content-type", "accept", "cookie"]) {
    const v = request.headers.get(name);
    if (v) headers.set(name, v);
  }

  const hasBody = !["GET", "HEAD", "DELETE"].includes(request.method);

  let body: BodyInit | null = null;
  if (hasBody) {
    // arrayBuffer préserve les fichiers binaires (uploads photo) et le JSON
    const buf = await request.arrayBuffer();
    if (buf.byteLength > 0) body = buf;
  }

  try {
    const res = await fetch(target, {
      method: request.method,
      headers,
      body,
      // @ts-ignore — nécessaire pour le streaming dans Node.js 18+
      duplex: "half",
    });

    const resBody = await res.arrayBuffer();
    const out = new NextResponse(resBody, { status: res.status });
    const ct = res.headers.get("content-type");
    if (ct) out.headers.set("content-type", ct);
    return out;
  } catch (err) {
    console.error("[proxy] Erreur vers", target, err);
    return NextResponse.json({ detail: "Service API inaccessible" }, { status: 503 });
  }
}

type Ctx = { params: Promise<{ path: string[] }> };

export async function GET(request: NextRequest, ctx: Ctx) {
  const { path } = await ctx.params;
  return forward(request, path);
}
export async function POST(request: NextRequest, ctx: Ctx) {
  const { path } = await ctx.params;
  return forward(request, path);
}
export async function PUT(request: NextRequest, ctx: Ctx) {
  const { path } = await ctx.params;
  return forward(request, path);
}
export async function PATCH(request: NextRequest, ctx: Ctx) {
  const { path } = await ctx.params;
  return forward(request, path);
}
export async function DELETE(request: NextRequest, ctx: Ctx) {
  const { path } = await ctx.params;
  return forward(request, path);
}
