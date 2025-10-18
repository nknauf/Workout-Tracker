
"use client"

import type React from "react"
import { useState, useRef, useEffect, useCallback } from "react"

// BEGIN: REPDECK_COMPONENT

// Types
type Post = {
  id: number | string
  author: { username: string; avatarUrl?: string }
  createdAt: string
  type: "image" | "video" | "text"
  mediaUrl?: string
  content?: string
  meal?: { name: string; protein: number; carbs: number; fats: number }
  workout?: { name: string; sets: number; reps: string }
  liked?: boolean
  comments?: { user: string; text: string; when: string }[]
}

type Props = {
  posts?: Post[]
  onToggleLike?: (id: Post["id"], liked: boolean) => void
}

// Mock data
const MOCK_POSTS: Post[] = [
  {
    id: 1,
    author: { username: "fitpro_mike", avatarUrl: "/fitness-avatar.jpg" },
    createdAt: "2h ago",
    type: "image",
    mediaUrl: "/gym-workout-video.jpg",
    workout: { name: "Bench Press", sets: 4, reps: "8-10" },
    liked: false,
    comments: [
      { user: "sarah_lifts", text: "Great form! 💪", when: "1h ago" },
      { user: "coach_dan", text: "Keep it up!", when: "45m ago" },
    ],
  },
  {
    id: 2,
    author: { username: "meal_prep_queen", avatarUrl: "/chef-avatar.png" },
    createdAt: "5h ago",
    type: "image",
    mediaUrl: "/healthy-meal-prep.png",
    meal: { name: "Chicken & Rice Bowl", protein: 45, carbs: 60, fats: 12 },
    liked: true,
    comments: [{ user: "nutrition_nerd", text: "Perfect macros!", when: "3h ago" }],
  },
  {
    id: 3,
    author: { username: "cardio_king", avatarUrl: "/runner-avatar.png" },
    createdAt: "1d ago",
    type: "image",
    mediaUrl: "/running-cardio.jpg",
    workout: { name: "HIIT Sprints", sets: 6, reps: "30s on / 30s off" },
    liked: false,
    comments: [],
  },
  {
    id: 4,
    author: { username: "motivation_daily", avatarUrl: "/motivational-avatar.jpg" },
    createdAt: "2d ago",
    type: "text",
    content:
      "Remember: Progress over perfection. Every rep counts, every meal matters. You're building the best version of yourself one day at a time. 💯",
    liked: true,
    comments: [
      { user: "inspired_joe", text: "Needed this today 🙏", when: "1d ago" },
      { user: "gym_rat_99", text: "Facts!", when: "1d ago" },
    ],
  },
]

// Hook for panel snapping
function useSnapScroller(containerRef: React.RefObject<HTMLDivElement>) {
  const scrollToPanel = useCallback(
    (index: number) => {
      if (!containerRef.current) return
      const panel = containerRef.current.children[index] as HTMLElement
      if (panel) {
        panel.scrollIntoView({ behavior: "smooth", inline: "start", block: "nearest" })
      }
    },
    [containerRef],
  )

  return { scrollToPanel }
}

// Single Post Card Component
function PostCard({
  post,
  onToggleLike,
}: {
  post: Post
  onToggleLike: (id: Post["id"], liked: boolean) => void
}) {
  const [currentPanel, setCurrentPanel] = useState(0)
  const panelContainerRef = useRef<HTMLDivElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const cardRef = useRef<HTMLDivElement>(null)
  const { scrollToPanel } = useSnapScroller(panelContainerRef)

  // Gesture detection
  const gestureRef = useRef({
    startX: 0,
    startY: 0,
    startTime: 0,
    isGesturing: false,
  })

  const handlePointerDown = (e: React.PointerEvent) => {
    gestureRef.current = {
      startX: e.clientX,
      startY: e.clientY,
      startTime: Date.now(),
      isGesturing: true,
    }
  }

  const handlePointerMove = (e: React.PointerEvent) => {
    if (!gestureRef.current.isGesturing) return

    const dx = e.clientX - gestureRef.current.startX
    const dy = e.clientY - gestureRef.current.startY
    if (Math.abs(dx) > 30 && Math.abs(dx) > Math.abs(dy)) {
      e.preventDefault()
    }
  }

  const handlePointerUp = (e: React.PointerEvent) => {
    if (!gestureRef.current.isGesturing) return
    const dx = e.clientX - gestureRef.current.startX
    const dy = e.clientY - gestureRef.current.startY

    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 2) {
      if (dx > 0 && currentPanel > 0) {
        setCurrentPanel(currentPanel - 1)
        scrollToPanel(currentPanel - 1)
      } else if (dx < 0 && currentPanel < 3) {
        setCurrentPanel(currentPanel + 1)
        scrollToPanel(currentPanel + 1)
      }
    }

    gestureRef.current.isGesturing = false
  }

  // Video autoplay with IntersectionObserver
  useEffect(() => {
    if (post.type !== "video" || !videoRef.current || !cardRef.current) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && entry.intersectionRatio >= 0.6) {
            videoRef.current?.play()
          } else {
            videoRef.current?.pause()
          }
        })
      },
      { threshold: [0.6] },
    )

    observer.observe(cardRef.current)
    return () => observer.disconnect()
  }, [post.type])

  return (
    <div
      ref={cardRef}
      className="h-screen scroll-snap-start flex flex-col items-center bg-white"
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
    >
      <div className="w-full max-w-md flex flex-col h-full border-x-2 border-b-2 border-black relative">
        {/* Header */}
        <div className="flex items-center gap-3 p-4 z-10 flex-shrink-0">
          <div className="w-10 h-10 rounded-full bg-gray-200 overflow-hidden border-2 border-black">
            {post.author.avatarUrl && (
              <img
                src={post.author.avatarUrl || "/placeholder.svg"}
                alt={post.author.username}
                className="w-full h-full object-cover"
              />
            )}
          </div>
          <div>
            <p className="font-bold text-sm">{post.author.username}</p>
            <p className="text-xs text-gray-600">{post.createdAt}</p>
          </div>
        </div>

        {/* Horizontal Panels */}
        <div
          ref={panelContainerRef}
          className="flex overflow-x-auto scroll-snap-x mandatory scrollbar-hide h-[60vh]"
          style={{ scrollbarWidth: "none" }}
        >
          {/* Panel 1 */}
          <div className="min-w-full scroll-snap-start flex items-center justify-center px-4">
            {post.type === "video" && post.mediaUrl && (
              <video
                ref={videoRef}
                src={post.mediaUrl}
                loop
                muted
                playsInline
                className="h-full w-full rounded-md border-2 border-black object-cover"
              />
            )}
            {post.type === "image" && post.mediaUrl && (
              <img
                src={post.mediaUrl || "/placeholder.svg"}
                alt="Post content"
                className="h-full w-full rounded-md border-2 border-black object-cover"
              />
            )}
            {post.type === "text" && (
              <div className="w-full p-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-md border-2 border-black">
                <p className="text-xl leading-relaxed font-medium">{post.content}</p>
              </div>
            )}
          </div>

          {/* Panel 2 */}
          <div className="min-w-full scroll-snap-start flex items-center justify-center p-8">
            <div className="w-full bg-white rounded-md border-2 border-black p-6">
              <h3 className="text-2xl font-bold mb-6">Details</h3>
              {post.meal && (
                <div className="space-y-3">
                  <p className="text-lg font-semibold">{post.meal.name}</p>
                  <div className="grid grid-cols-3 gap-4 mt-4">
                    <div className="text-center p-3 bg-blue-50 rounded border border-blue-200">
                      <p className="text-2xl font-bold text-blue-600">{post.meal.protein}g</p>
                      <p className="text-xs text-gray-600 mt-1">Protein</p>
                    </div>
                    <div className="text-center p-3 bg-green-50 rounded border border-green-200">
                      <p className="text-2xl font-bold text-green-600">{post.meal.carbs}g</p>
                      <p className="text-xs text-gray-600 mt-1">Carbs</p>
                    </div>
                    <div className="text-center p-3 bg-yellow-50 rounded border border-yellow-200">
                      <p className="text-2xl font-bold text-yellow-600">{post.meal.fats}g</p>
                      <p className="text-xs text-gray-600 mt-1">Fats</p>
                    </div>
                  </div>
                </div>
              )}
              {post.workout && (
                <div className="space-y-3">
                  <p className="text-lg font-semibold">{post.workout.name}</p>
                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div className="text-center p-3 bg-purple-50 rounded border border-purple-200">
                      <p className="text-2xl font-bold text-purple-600">{post.workout.sets}</p>
                      <p className="text-xs text-gray-600 mt-1">Sets</p>
                    </div>
                    <div className="text-center p-3 bg-pink-50 rounded border border-pink-200">
                      <p className="text-lg font-bold text-pink-600">{post.workout.reps}</p>
                      <p className="text-xs text-gray-600 mt-1">Reps</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Panel 3 */}
          <div className="min-w-full scroll-snap-start flex items-start justify-center p-8 overflow-y-auto">
            <div className="w-full">
              <h3 className="text-2xl font-bold mb-6">Comments</h3>
              {post.comments && post.comments.length > 0 ? (
                <div className="space-y-4">
                  {post.comments.map((comment, idx) => (
                    <div key={idx} className="bg-white rounded-md border-2 border-black p-4">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full bg-gray-200 border border-black flex-shrink-0" />
                        <div className="flex-1">
                          <p className="font-bold text-sm">{comment.user}</p>
                          <p className="text-sm mt-1">{comment.text}</p>
                          <p className="text-xs text-gray-500 mt-1">{comment.when}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">No comments yet</p>
              )}
            </div>
          </div>

          {/* Panel 4 */}
          <div className="min-w-full scroll-snap-start flex items-center justify-center p-8">
            <div className="w-full space-y-4">
              <h3 className="text-2xl font-bold mb-6">Actions</h3>
              <button className="w-full p-4 bg-white rounded-md border-2 border-black font-semibold hover:bg-gray-50 transition-colors">
                📤 Share Post
              </button>
              <button className="w-full p-4 bg-white rounded-md border-2 border-black font-semibold hover:bg-gray-50 transition-colors">
                💾 Save to Collection
              </button>
              <button className="w-full p-4 bg-white rounded-md border-2 border-black font-semibold hover:bg-gray-50 transition-colors">
                🚫 Report
              </button>
            </div>
          </div>
        </div>

        <div className="absolute bottom-20 left-1/2 -translate-x-1/2 flex gap-6 z-10">
          <button
            onClick={() => onToggleLike(post.id, !post.liked)}
            className="w-14 h-14 rounded-full bg-white border-2 border-black flex items-center justify-center text-2xl hover:scale-110 transition-transform shadow-lg"
          >
            {post.liked ? "❤️" : "🤍"}
          </button>
          <button
            onClick={() => {
              setCurrentPanel(2)
              scrollToPanel(2)
            }}
            className="w-14 h-14 rounded-full bg-white border-2 border-black flex items-center justify-center text-2xl hover:scale-110 transition-transform shadow-lg"
          >
            💬
          </button>
        </div>

        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2 z-10">
          {[0, 1, 2, 3].map((idx) => (
            <div
              key={idx}
              className={`w-2 h-2 rounded-full transition-colors ${currentPanel === idx ? "bg-black" : "bg-gray-300"}`}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

// Main RepDeck Component
export default function RepDeck({ posts = MOCK_POSTS, onToggleLike }: Props) {
  const [postStates, setPostStates] = useState<Map<Post["id"], { liked: boolean }>>(
    new Map(posts.map((p) => [p.id, { liked: p.liked || false }])),
  )

  const handleToggleLike = useCallback(
    (id: Post["id"], liked: boolean) => {
      setPostStates((prev) => {
        const next = new Map(prev)
        const current = next.get(id) || { liked: false }
        next.set(id, { ...current, liked })
        return next
      })
      onToggleLike?.(id, liked)
    },
    [onToggleLike],
  )

  const enrichedPosts = posts.map((post) => ({
    ...post,
    liked: postStates.get(post.id)?.liked ?? post.liked ?? false,
  }))

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key.toLowerCase() === "l") e.preventDefault()
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [])

  return (
    <>
      <style jsx global>{`
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
      <div className="h-screen overflow-y-auto scroll-snap-y scroll-snap-type-mandatory bg-gray-100">
        {enrichedPosts.map((post) => (
          <PostCard key={post.id} post={post} onToggleLike={handleToggleLike} />
        ))}
      </div>
    </>
  )
}


// END: REPDECK_COMPONENT