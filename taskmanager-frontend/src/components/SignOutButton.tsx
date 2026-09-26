'use client'

import { createClient } from '@/utils/supabase/client'
import { useRouter } from 'next/navigation'

export default function SignOutButton() {
  const router = useRouter()

  const handleSignOut = async () => {
    const supabase = createClient()
    await supabase.auth.signOut()
    router.push('/')
    router.refresh()
  }

  return (
    <button
      onClick={handleSignOut}
      className="bg-white dark:bg-[#18181B] border border-[#E4E4E7] dark:border-[#27272A] text-[#18181B] dark:text-[#FAFAFA] hover:bg-[#FAFAFA] dark:hover:bg-[#27272A] text-sm font-medium px-3.5 py-1.5 rounded-[8px] transition-colors"
    >
      Sign out
    </button>
  )
}
