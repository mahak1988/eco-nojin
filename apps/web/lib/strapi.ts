const STRAPI_URL = process.env.NEXT_PUBLIC_STRAPI_URL || 'http://localhost:1337'

export async function getArticles() {
  const response = await fetch(`${STRAPI_URL}/api/articles?populate=*`, {
    next: { revalidate: 60 }, // Revalidate every 60 seconds
  })
  
  if (!response.ok) throw new Error('Failed to fetch articles')
  
  const data = await response.json()
  return data.data
}

export async function getArticleBySlug(slug: string) {
  const response = await fetch(
    `${STRAPI_URL}/api/articles?filters[slug][$eq]=${slug}&populate=*`,
    { next: { revalidate: 60 } }
  )
  
  if (!response.ok) throw new Error('Failed to fetch article')
  
  const data = await response.json()
  return data.data[0]
}

export async function getPages() {
  const response = await fetch(`${STRAPI_URL}/api/pages?populate=*`, {
    next: { revalidate: 60 },
  })
  
  if (!response.ok) throw new Error('Failed to fetch pages')
  
  const data = await response.json()
  return data.data
}