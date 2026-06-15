import { NextRequest, NextResponse } from "next/server";

const BACKEND_BASE_URL =
  process.env.BACKEND_BASE_URL || "http://127.0.0.1:8000";

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => null);

  try {
    const res = await fetch(`${BACKEND_BASE_URL}/soil-water/analyses`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const text = await res.text();
    if (!res.ok) {
      return new NextResponse(text || "Backend error", { status: res.status });
    }

    const contentType = res.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      return NextResponse.json(JSON.parse(text), { status: res.status });
    }
    return new NextResponse(text, { status: res.status });
  } catch (err: any) {
    console.error("Error proxying to backend:", err);
    return new NextResponse(
      "Proxy error to backend (is FastAPI running on BACKEND_BASE_URL?)",
      { status: 502 },
    );
  }
}
