'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/utils/supabase/client'
import { apiFetch } from '@/utils/api'
import SignOutButton from '@/components/SignOutButton'
import ThemeToggle from '@/components/ThemeToggle'

interface Task {
  id: string
  title: string
  description?: string
  status: 'todo' | 'in_progress' | 'done'
  created_by: string
  assigned_to?: string
  created_at: string
  completed_at?: string
}

interface UserProfile {
  id: string
  email: string
  full_name?: string
}

export default function DashboardPage() {
  const router = useRouter()
  const [currentUser, setCurrentUser] = useState<{ id: string; email?: string; name?: string } | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [users, setUsers] = useState<UserProfile[]>([])
  const [loading, setLoading] = useState(true)

  // Filter state
  const [filter, setFilter] = useState<'all' | 'assigned' | 'created'>('all')

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [assignedTo, setAssignedTo] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const fetchTasks = useCallback(async () => {
    try {
      const res = await apiFetch('/api/tasks')
      if (res.ok) {
        const data = await res.json()
        setTasks(data)
      }
    } catch (err) {
      console.error('Failed to fetch tasks:', err)
    }
  }, [])

  const fetchUsers = useCallback(async () => {
    try {
      const res = await apiFetch('/api/users')
      if (res.ok) {
        const data = await res.json()
        setUsers(data)
      }
    } catch (err) {
      console.error('Failed to fetch users:', err)
    }
  }, [])

  useEffect(() => {
    const init = async () => {
      const supabase = createClient()
      const {
        data: { user },
      } = await supabase.auth.getUser()

      if (!user) {
        router.push('/')
        return
      }

      setCurrentUser({
        id: user.id,
        email: user.email,
        name: user.user_metadata?.full_name || user.user_metadata?.name || 'User',
      })

      await Promise.all([fetchTasks(), fetchUsers()])
      setLoading(false)
    }

    init()
  }, [router, fetchTasks, fetchUsers])

  const handleMarkAsDone = async (taskId: string) => {
    try {
      const res = await apiFetch(`/api/tasks/${taskId}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: 'done' }),
      })
      if (res.ok) {
        await fetchTasks()
      }
    } catch (err) {
      console.error('Failed to update task:', err)
    }
  }

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return

    setIsSubmitting(true)
    try {
      const res = await apiFetch('/api/tasks', {
        method: 'POST',
        body: JSON.stringify({
          title,
          description,
          assigned_to: assignedTo || null,
        }),
      })

      if (res.ok) {
        setTitle('')
        setDescription('')
        setAssignedTo('')
        setIsModalOpen(false)
        await fetchTasks()
      }
    } catch (err) {
      console.error('Failed to create task:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const getAssigneeInfo = (assignedToId?: string) => {
    if (!assignedToId) return { name: 'Unassigned', initial: 'U' }
    const match = users.find((u) => u.id === assignedToId)
    if (!match) return { name: 'Unknown user', initial: '?' }
    const name = match.full_name || match.email
    const initial = name.charAt(0).toUpperCase()
    return { name, initial }
  }

  const renderStatusBadge = (status: Task['status']) => {
    switch (status) {
      case 'done':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#DCFCE7] dark:bg-[#052E16] text-[#15803D] dark:text-[#4ADE80]">
            Done
          </span>
        )
      case 'in_progress':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#FEF3C7] dark:bg-[#422006] text-[#B45309] dark:text-[#FCD34D]">
            In progress
          </span>
        )
      case 'todo':
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#F4F4F5] dark:bg-[#27272A] text-[#71717A] dark:text-[#A1A1AA]">
            Todo
          </span>
        )
    }
  }

  const filteredTasks = tasks.filter((task) => {
    if (filter === 'assigned') return task.assigned_to === currentUser?.id
    if (filter === 'created') return task.created_by === currentUser?.id
    return true
  })

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAFAFA] dark:bg-[#0A0A0B] text-[#71717A] dark:text-[#A1A1AA] transition-colors">
        <p className="text-sm font-medium">Loading dashboard...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#FAFAFA] dark:bg-[#0A0A0B] text-[#18181B] dark:text-[#FAFAFA] p-6 md:p-10 transition-colors">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <header className="flex items-center justify-between bg-white dark:bg-[#18181B] p-6 rounded-[8px] border border-[#E4E4E7] dark:border-[#27272A] transition-colors">
          <div className="space-y-0.5 text-left">
            <h1 className="text-xl font-semibold text-[#18181B] dark:text-[#FAFAFA]">{currentUser?.name}</h1>
            <p className="text-sm text-[#71717A] dark:text-[#A1A1AA]">{currentUser?.email}</p>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <SignOutButton />
          </div>
        </header>

        {/* Tasks Section */}
        <main className="bg-white dark:bg-[#18181B] p-6 rounded-[8px] border border-[#E4E4E7] dark:border-[#27272A] space-y-6 transition-colors">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <h2 className="text-lg font-semibold text-[#18181B] dark:text-[#FAFAFA] text-left">My tasks</h2>
            <button
              onClick={() => setIsModalOpen(true)}
              className="bg-[#2952E3] dark:bg-[#4F6EF7] hover:bg-[#2042C7] dark:hover:bg-[#3B5DE7] text-white px-3.5 py-1.5 rounded-[8px] font-medium text-sm transition-colors self-start sm:self-auto"
            >
              Create task
            </button>
          </div>

          {/* Filter Tabs */}
          <div className="flex items-center gap-1 border-b border-[#E4E4E7] dark:border-[#27272A] pb-3">
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1.5 rounded-[6px] text-xs font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-[#F4F4F5] dark:bg-[#27272A] text-[#18181B] dark:text-[#FAFAFA]'
                  : 'text-[#71717A] dark:text-[#A1A1AA] hover:text-[#18181B] dark:hover:text-[#FAFAFA]'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilter('assigned')}
              className={`px-3 py-1.5 rounded-[6px] text-xs font-medium transition-colors ${
                filter === 'assigned'
                  ? 'bg-[#F4F4F5] dark:bg-[#27272A] text-[#18181B] dark:text-[#FAFAFA]'
                  : 'text-[#71717A] dark:text-[#A1A1AA] hover:text-[#18181B] dark:hover:text-[#FAFAFA]'
              }`}
            >
              Assigned to me
            </button>
            <button
              onClick={() => setFilter('created')}
              className={`px-3 py-1.5 rounded-[6px] text-xs font-medium transition-colors ${
                filter === 'created'
                  ? 'bg-[#F4F4F5] dark:bg-[#27272A] text-[#18181B] dark:text-[#FAFAFA]'
                  : 'text-[#71717A] dark:text-[#A1A1AA] hover:text-[#18181B] dark:hover:text-[#FAFAFA]'
              }`}
            >
              Created by me
            </button>
          </div>

          {/* Task List or Empty State */}
          {filteredTasks.length === 0 ? (
            <div className="py-12 text-center space-y-2">
              <div className="w-10 h-10 rounded-full bg-[#F4F4F5] dark:bg-[#27272A] text-[#71717A] dark:text-[#A1A1AA] flex items-center justify-center mx-auto mb-3">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h3 className="text-sm font-semibold text-[#18181B] dark:text-[#FAFAFA]">No tasks found</h3>
              <p className="text-xs text-[#71717A] dark:text-[#A1A1AA]">
                {filter === 'all'
                  ? "You don't have any tasks yet. Click 'Create task' to get started!"
                  : filter === 'assigned'
                  ? "No tasks are currently assigned to you."
                  : "You haven't created any tasks yet."}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredTasks.map((task) => {
                const assignee = getAssigneeInfo(task.assigned_to)
                return (
                  <div
                    key={task.id}
                    className="flex items-start justify-between p-4 border border-[#E4E4E7] dark:border-[#27272A] bg-white dark:bg-[#18181B] rounded-[8px] hover:border-[#D4D4D8] dark:hover:border-[#3F3F46] transition-colors text-left"
                  >
                    <div className="space-y-2 max-w-xl">
                      <div className="flex items-center gap-3">
                        <h3 className="font-semibold text-sm text-[#18181B] dark:text-[#FAFAFA]">{task.title}</h3>
                        {renderStatusBadge(task.status)}
                      </div>
                      {task.description && (
                        <p className="text-sm text-[#71717A] dark:text-[#A1A1AA]">{task.description}</p>
                      )}
                      
                      {/* Assignee Avatar */}
                      <div className="flex items-center gap-1.5 text-xs text-[#71717A] dark:text-[#A1A1AA]">
                        <span>Assigned to</span>
                        <div className="flex items-center gap-1">
                          <span className="w-4 h-4 rounded-full bg-[#2952E3] dark:bg-[#4F6EF7] text-white text-[10px] font-semibold flex items-center justify-center shrink-0">
                            {assignee.initial}
                          </span>
                          <span className="font-medium text-[#18181B] dark:text-[#FAFAFA]">{assignee.name}</span>
                        </div>
                      </div>
                    </div>

                    {task.status !== 'done' && (
                      <button
                        onClick={() => handleMarkAsDone(task.id)}
                        className="bg-[#2952E3] dark:bg-[#4F6EF7] hover:bg-[#2042C7] dark:hover:bg-[#3B5DE7] text-white text-xs px-3 py-1.5 rounded-[8px] font-medium transition-colors ml-4 shrink-0"
                      >
                        Mark as done
                      </button>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </main>
      </div>

      {/* Create Task Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-[#18181B] rounded-[8px] border border-[#E4E4E7] dark:border-[#27272A] max-w-md w-full p-6 space-y-5 text-left transition-colors">
            <h3 className="text-lg font-semibold text-[#18181B] dark:text-[#FAFAFA]">Create task</h3>
            <form onSubmit={handleCreateTask} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-[#71717A] dark:text-[#A1A1AA] mb-1.5">Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Task title"
                  className="w-full border border-[#E4E4E7] dark:border-[#27272A] px-3 py-2 rounded-[8px] text-sm text-[#18181B] dark:text-[#FAFAFA] bg-white dark:bg-[#18181B] focus:outline-none focus:border-[#2952E3] dark:focus:border-[#4F6EF7] focus:ring-1 focus:ring-[#2952E3] dark:focus:ring-[#4F6EF7]"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-[#71717A] dark:text-[#A1A1AA] mb-1.5">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Task description"
                  rows={3}
                  className="w-full border border-[#E4E4E7] dark:border-[#27272A] px-3 py-2 rounded-[8px] text-sm text-[#18181B] dark:text-[#FAFAFA] bg-white dark:bg-[#18181B] focus:outline-none focus:border-[#2952E3] dark:focus:border-[#4F6EF7] focus:ring-1 focus:ring-[#2952E3] dark:focus:ring-[#4F6EF7]"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-[#71717A] dark:text-[#A1A1AA] mb-1.5">Assignee</label>
                <select
                  value={assignedTo}
                  onChange={(e) => setAssignedTo(e.target.value)}
                  className="w-full border border-[#E4E4E7] dark:border-[#27272A] px-3 py-2 rounded-[8px] text-sm text-[#18181B] dark:text-[#FAFAFA] bg-white dark:bg-[#18181B] focus:outline-none focus:border-[#2952E3] dark:focus:border-[#4F6EF7] focus:ring-1 focus:ring-[#2952E3] dark:focus:ring-[#4F6EF7]"
                >
                  <option value="" className="text-[#18181B] dark:text-[#FAFAFA] bg-white dark:bg-[#18181B]">Select assignee (optional)</option>
                  {users.map((user) => (
                    <option key={user.id} value={user.id} className="text-[#18181B] dark:text-[#FAFAFA] bg-white dark:bg-[#18181B]">
                      {user.full_name ? `${user.full_name} (${user.email})` : user.email}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-3.5 py-1.5 text-sm font-medium text-[#18181B] dark:text-[#FAFAFA] border border-[#E4E4E7] dark:border-[#27272A] rounded-[8px] bg-white dark:bg-[#18181B] hover:bg-[#FAFAFA] dark:hover:bg-[#27272A] transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-3.5 py-1.5 text-sm font-medium text-white bg-[#2952E3] dark:bg-[#4F6EF7] hover:bg-[#2042C7] dark:hover:bg-[#3B5DE7] rounded-[8px] transition-colors disabled:opacity-50"
                >
                  {isSubmitting ? 'Creating...' : 'Create task'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
