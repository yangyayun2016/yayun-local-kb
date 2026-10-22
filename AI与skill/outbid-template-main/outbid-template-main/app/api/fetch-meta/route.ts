import { NextRequest, NextResponse } from "next/server"

interface MetaData {
  favicon: string
  title: string
  description: string
}

async function fetchMetaData(url: string): Promise<MetaData> {
  const hostname = new URL(url).hostname
  
  const favicon = `https://www.google.com/s2/favicons?domain=${hostname}&sz=32`
  
  try {
    const response = await fetch(url, {
      headers: {
        "User-Agent": "Mozilla/5.0 (compatible; MetaFetcher/1.0)",
      },
      signal: AbortSignal.timeout(5000),
    })
    
    const html = await response.text()
    
    const titleMatch = html.match(/<title[^>]*>([^<]+)<\/title>/i)
    const title = titleMatch ? titleMatch[1].trim() : hostname
    
    const descMatch = html.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']+)["']/i)
      || html.match(/<meta[^>]*content=["']([^"']+)["'][^>]*name=["']description["']/i)
    const description = descMatch ? descMatch[1].trim() : ""
    
    return { favicon, title, description }
  } catch {
    return { favicon, title: hostname, description: "" }
  }
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const url = searchParams.get("url")
  
  if (!url) {
    return NextResponse.json({ error: "URL is required" }, { status: 400 })
  }
  
  try {
    new URL(url)
  } catch {
    return NextResponse.json({ error: "Invalid URL" }, { status: 400 })
  }
  
  const metaData = await fetchMetaData(url)
  return NextResponse.json(metaData)
}