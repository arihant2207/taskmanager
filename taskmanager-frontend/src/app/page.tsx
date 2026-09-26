'use client'

import { createClient } from '@/utils/supabase/client'

export default function Home() {
  const supabase = createClient()

  const handleLogin = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
        queryParams: {
          prompt: 'select_account',
        },
      },
    })
  }

  return (
    <div className="min-h-screen flex w-full bg-[#FAFAFA] text-[#18181B]">
      {/* LEFT COLUMN - Desktop Only (55% width) */}
      <div className="hidden md:flex md:w-[55%] relative flex-col justify-between bg-[#2952E3] text-white p-10 lg:p-14 overflow-hidden">
        {/* CSS-only Dot Grid Pattern */}
        <div 
          className="absolute inset-0 pointer-events-none opacity-[0.08]"
          style={{
            backgroundImage: 'radial-gradient(#ffffff 1px, transparent 1px)',
            backgroundSize: '20px 20px',
          }}
        />

        {/* Top Logomark */}
        <div className="relative z-10 flex items-center gap-3">
          <div className="w-10 h-10 bg-white rounded-[10px] flex items-center justify-center text-[#2952E3] font-bold select-none">
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>
          <span className="font-semibold text-lg tracking-tight text-white">Task Manager</span>
        </div>

        {/* Hero Copy (Vertically Centered) */}
        <div className="relative z-10 my-auto space-y-3 max-w-lg text-left">
          <h1 className="text-3xl lg:text-4xl font-semibold leading-tight text-white">
            Task Manager
          </h1>
          <p className="text-base lg:text-lg text-white/80 font-normal leading-relaxed">
            Create, assign, and track tasks — with your team, in one place.
          </p>
        </div>

        {/* Bottom Footer / Copyright */}
        <div className="relative z-10 text-xs text-white/60 text-left font-normal">
          © {new Date().getFullYear()} Task Manager. All rights reserved.
        </div>
      </div>

      {/* RIGHT COLUMN - Form Panel (45% width on desktop, 100% on mobile) */}
      <div className="w-full md:w-[45%] flex flex-col items-center justify-center p-6 md:p-12 bg-[#FAFAFA]">
        {/* Mobile Branding (Visible only below md) */}
        <div className="flex md:hidden items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-[#2952E3] text-white rounded-[10px] flex items-center justify-center font-bold text-xl select-none">
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>
          <span className="font-semibold text-xl tracking-tight text-[#18181B]">Task Manager</span>
        </div>

        {/* Sign-in Card */}
        <div className="w-full max-w-sm bg-white border border-[#E4E4E7] rounded-[8px] p-6 space-y-6 text-left">
          <div className="space-y-1 text-left">
            <h2 className="text-xl font-semibold text-[#18181B]">Welcome back</h2>
            <p className="text-sm text-[#71717A]">Sign in to manage your tasks and projects.</p>
          </div>

          <button
            onClick={handleLogin}
            className="w-full bg-[#2952E3] hover:bg-[#2042C7] text-white px-4 py-2.5 rounded-[8px] font-medium text-sm transition-colors flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="currentColor"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="currentColor"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="currentColor"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
            Sign in with Google
          </button>
        </div>
      </div>
    </div>
  )
}
