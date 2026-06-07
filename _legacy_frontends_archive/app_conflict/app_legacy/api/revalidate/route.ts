import { NextRequest, NextResponse } from 'next/server'
import { revalidatePath } from 'next/cache'

export async function POST(request: NextRequest) {
  const secret = request.headers.get('x-strapi-webhook-secret')
  
  if (secret !== process.env.STRAPI_WEBHOOK_SECRET) {
    return NextResponse.json({ error: 'Invalid secret' }, { status: 401 })
  }

  const body = await request.json()
  const { model, entry } = body

  if (model === 'article') {
    revalidatePath('/blog')
    revalidatePath(`/blog/${entry.slug}`)
  } else if (model === 'page') {
    revalidatePath(`/pages/${entry.slug}`)
  }

  return NextResponse.json({ revalidated: true, now: Date.now() })
}