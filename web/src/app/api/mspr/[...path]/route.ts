import { NextRequest, NextResponse } from "next/server";

function backendBase(): string {
  return (process.env.API_URL || "http://127.0.0.1:8001").replace(/\/$/, "");
}

async function forward(
  request: NextRequest,
  segments: string[],
): Promise<NextResponse> {
  const path = segments.join("/");
  const u = new URL(request.url);
  const target = `${backendBase()}/api/v1/${path}${u.search}`;

  const headers = new Headers();
  for (const name of ["authorization", "content-type", "accept"]) {
    const v = request.headers.get(name);
    if (v) headers.set(name, v);
  }

  const init: RequestInit = {
    method: request.method,
    headers,
  };

  if (!["GET", "HEAD", "DELETE"].includes(request.method)) {
    const body = await request.arrayBuffer();
    if (body.byteLength) init.body = body;
  }

  const res = await fetch(target, init);
  const out = new NextResponse(await res.arrayBuffer(), {
    status: res.status,
  });
  const ct = res.headers.get("content-type");
  if (ct) out.headers.set("content-type", ct);
  return out;
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
