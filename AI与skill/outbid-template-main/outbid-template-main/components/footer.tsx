"use client"

import Link from "next/link"
import { Separator } from "@/components/ui/separator"

export function Footer() {
  return (
    <footer className="mt-auto">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Separator className="mb-6" />
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
          <p>
            Built by <Link href="https://aniketpawar.com?utm_source=outbid&utm_medium=footer&utm_campaign=attribution" target="_blank" rel="noopener noreferrer" className="underline hover:text-foreground">Aniket Pawar</Link>
          </p>
          <div className="flex items-center gap-4">
            <Link href="/stats" className="hover:text-foreground transition-colors">Live stats</Link>
            <Link href="/friends" className="hover:text-foreground transition-colors">Friends</Link>
            <span>Inspired by <a href="https://outbid.lol?utm_source=outbid&utm_medium=footer&utm_campaign=inspiration" target="_blank" rel="noopener noreferrer" className="underline hover:text-foreground transition-colors">outbid.lol</a></span>
          </div>
        </div>
      </div>
    </footer>
  )
}