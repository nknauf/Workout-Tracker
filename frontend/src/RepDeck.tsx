
"use client"

import type React from "react"
import { useState, useRef, useEffect, useCallback, useMemo } from "react"

// BEGIN: REPDECK_COMPONENT

// Types
export type Media = { url: string; alt?: string }

export type Post = {
  id: number | string
  author: { username: string; avatarUrl?: string }
  createdAt: string
  type: "image" | "video" | "text"
  mediaUrl?: string
  images?: Media[]
  content?: string
  meal?: { name: string; protein: number; carbs: number; fats: number }
  workout?: { name: string; sets: number; reps: string }
  liked?: boolean
  likeCount?: number
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
    images: [
      { url: "/gym-workout-video.jpg", alt: "Bench press set" },
      { url: "/gym-workout-detail.jpg", alt: "Bench setup closeup" },
    ],
    workout: { name: "Bench Press", sets: 4, reps: "8-10" },
    liked: false,
    likeCount: 18,
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
    images: [{ url: "/healthy-meal-prep.png", alt: "Chicken rice bowl" }],
    meal: { name: "Chicken & Rice Bowl", protein: 45, carbs: 60, fats: 12 },
    liked: true,
    likeCount: 42,
    comments: [{ user: "nutrition_nerd", text: "Perfect macros!", when: "3h ago" }],
  },
  {
    id: 3,
    author: { username: "cardio_king", avatarUrl: "/runner-avatar.png" },
    createdAt: "1d ago",
    type: "image",
    mediaUrl: "/running-cardio.jpg",
    images: [{ url: "/running-cardio.jpg", alt: "Track workout" }],
    workout: { name: "HIIT Sprints", sets: 6, reps: "30s on / 30s off" },
    liked: false,
    likeCount: 7,
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
    likeCount: 64,
    comments: [
      { user: "inspired_joe", text: "Needed this today 🙏", when: "1d ago" },
      { user: "gym_rat_99", text: "Facts!", when: "1d ago" },
    ],
  },
]

// Hook for panel snapping
function useSnapScroller(containerRef: React.RefObject<HTMLDivElement>, panelCount: number) {
  const [activeIndex, setActiveIndex] = useState(0)

  const scrollToPanel = useCallback(
    (index: number) => {
      if (!containerRef.current) return
      const bounded = Math.min(Math.max(index, 0), panelCount - 1)
      const target = containerRef.current.children[bounded] as HTMLElement | undefined
      if (target) {
        target.scrollIntoView({ behavior: "smooth", inline: "start", block: "nearest" })
      }
      setActiveIndex(bounded)
    },
    [containerRef, panelCount],
  )

  useEffect(() => {
    const node = containerRef.current
    if (!node) return

    const handleScroll = () => {
      const width = node.clientWidth || 1
      const rawIndex = Math.round(node.scrollLeft / width)
      const bounded = Math.min(Math.max(rawIndex, 0), panelCount - 1)
      setActiveIndex(bounded)
    }

    node.addEventListener("scroll", handleScroll, { passive: true })
    return () => node.removeEventListener("scroll", handleScroll)
  }, [containerRef, panelCount])

  return { scrollToPanel, activeIndex }
}

function MediaPanel({ post, videoRef }: { post: Post; videoRef: React.RefObject<HTMLVideoElement> }) {
  const images = useMemo<Media[]>(() => {
    if (post.images && post.images.length > 0) {
      return post.images
    }
    if (post.mediaUrl) {
      return [{ url: post.mediaUrl, alt: post.content?.slice(0, 80) }]
    }
    return []
  }, [post.images, post.mediaUrl, post.content])

  const galleryRef = useRef<HTMLDivElement>(null)
  const [imageIndex, setImageIndex] = useState(0)
  const hasGallery = images.length > 1

  const scrollToImage = useCallback(
    (index: number) => {
      if (!galleryRef.current) return
      const bounded = Math.min(Math.max(index, 0), images.length - 1)
      galleryRef.current.scrollTo({
        left: bounded * galleryRef.current.clientWidth,
        behavior: "smooth",
      })
      setImageIndex(bounded)
    },
    [images.length],
  )

  useEffect(() => {
    setImageIndex(0)
    if (galleryRef.current) {
      galleryRef.current.scrollTo({ left: 0 })
    }
  }, [post.id])

  useEffect(() => {
    if (!hasGallery || !galleryRef.current) return
    const node = galleryRef.current
    const handleScroll = () => {
      const width = node.clientWidth || 1
      const rawIndex = Math.round(node.scrollLeft / width)
      const bounded = Math.min(Math.max(rawIndex, 0), images.length - 1)
      setImageIndex(bounded)
    }
    node.addEventListener("scroll", handleScroll, { passive: true })
    return () => node.removeEventListener("scroll", handleScroll)
  }, [hasGallery, images.length])

  if (post.type === "video" && post.mediaUrl) {
    return (
      <video
        ref={videoRef}
        src={post.mediaUrl}
        loop
        muted
        playsInline
        className="h-full w-full rounded-md border-2 border-black object-cover"
      />
    )
  }

  if (images.length > 0) {
    if (hasGallery) {
      return (
        <div className="relative h-full w-full">
          <div
            ref={galleryRef}
            className="flex h-full w-full overflow-x-auto snap-x snap-mandatory scrollbar-hide"
          >
            {images.map((media, index) => (
              <div
                key={`${media.url}-${index}`}
                className="flex h-full w-full flex-shrink-0 items-center justify-center px-4 snap-center"
              >
                <img
                  src={media.url || "/placeholder.svg"}
                  alt={media.alt || "Post image"}
                  className="h-full w-full rounded-md border-2 border-black object-cover"
                />
              </div>
            ))}
          </div>
          <div className="absolute bottom-4 left-1/2 flex -translate-x-1/2 gap-2">
            {images.map((_, index) => (
              <button
                key={index}
                type="button"
                onClick={() => scrollToImage(index)}
                className={`h-2 w-2 rounded-full transition-colors ${
                  imageIndex === index ? "bg-black" : "bg-gray-300"
                }`}
                aria-label={`Show image ${index + 1} of ${images.length}`}
              />
            ))}
          </div>
        </div>
      )
    }

    const [media] = images
    return (
      <img
        src={media.url || "/placeholder.svg"}
        alt={media.alt || "Post image"}
        className="h-full w-full rounded-md border-2 border-black object-cover"
      />
    )
  }

  return (
    <div className="w-full rounded-md border-2 border-black bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <p className="text-xl leading-relaxed font-medium">{post.content || ""}</p>
    </div>
  )
}

// Single Post Card Component
function PostCard({
  post,
  onToggleLike,
}: {
  post: Post
  onToggleLike: (id: Post["id"], liked: boolean) => void
}) {
  const panelContainerRef = useRef<HTMLDivElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const cardRef = useRef<HTMLDivElement>(null)
  const { scrollToPanel, activeIndex: currentPanel } = useSnapScroller(panelContainerRef, 3)

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
    <div ref={cardRef} className="flex h-screen flex-col items-center bg-white scroll-snap-start">
      <div className="relative flex h-full w-full max-w-md flex-col border-b-2 border-x-2 border-black">
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
          className="scrollbar-hide flex h-[60vh] overflow-x-auto snap-x snap-mandatory"
        >
          <div className="flex min-w-full items-center justify-center px-4">
            <MediaPanel post={post} videoRef={videoRef} />
          </div>

          <div className="flex min-w-full items-center justify-center p-8">
            <div className="w-full rounded-md border-2 border-black bg-white p-6">
              <h3 className="mb-6 text-2xl font-bold">Details</h3>
              {post.meal && (
                <div className="space-y-3">
                  <p className="text-lg font-semibold">{post.meal.name}</p>
                  <div className="mt-4 grid grid-cols-3 gap-4">
                    <div className="rounded border border-blue-200 bg-blue-50 p-3 text-center">
                      <p className="text-2xl font-bold text-blue-600">{post.meal.protein}g</p>
                      <p className="mt-1 text-xs text-gray-600">Protein</p>
                    </div>
                    <div className="rounded border border-green-200 bg-green-50 p-3 text-center">
                      <p className="text-2xl font-bold text-green-600">{post.meal.carbs}g</p>
                      <p className="mt-1 text-xs text-gray-600">Carbs</p>
                    </div>
                    <div className="rounded border border-yellow-200 bg-yellow-50 p-3 text-center">
                      <p className="text-2xl font-bold text-yellow-600">{post.meal.fats}g</p>
                      <p className="mt-1 text-xs text-gray-600">Fats</p>
                    </div>
                  </div>
                </div>
              )}
              {post.workout && (
                <div className="space-y-3">
                  <p className="text-lg font-semibold">{post.workout.name}</p>
                  <div className="mt-4 grid grid-cols-2 gap-4">
                    <div className="rounded border border-purple-200 bg-purple-50 p-3 text-center">
                      <p className="text-2xl font-bold text-purple-600">{post.workout.sets}</p>
                      <p className="mt-1 text-xs text-gray-600">Sets</p>
                    </div>
                    <div className="rounded border border-pink-200 bg-pink-50 p-3 text-center">
                      <p className="text-lg font-bold text-pink-600">{post.workout.reps}</p>
                      <p className="mt-1 text-xs text-gray-600">Reps</p>
                    </div>
                  </div>
                </div>
              )}
              {!post.meal && !post.workout && (
                <p className="text-sm text-gray-500">No additional details.</p>
              )}
            </div>
          </div>

          <div className="flex min-w-full items-start justify-center overflow-y-auto p-8">
            <div className="w-full">
              <h3 className="mb-6 text-2xl font-bold">Comments</h3>
              {post.comments && post.comments.length > 0 ? (
                <div className="space-y-4">
                  {post.comments.map((comment, idx) => (
                    <div key={idx} className="rounded-md border-2 border-black bg-white p-4">
                      <div className="flex items-start gap-3">
                        <div className="h-8 w-8 flex-shrink-0 rounded-full border border-black bg-gray-200" />
                        <div className="flex-1">
                          <p className="text-sm font-bold">{comment.user}</p>
                          <p className="mt-1 text-sm">{comment.text}</p>
                          <p className="mt-1 text-xs text-gray-500">{comment.when}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="py-8 text-center text-gray-500">No comments yet</p>
              )}
            </div>
          </div>
        </div>

        <div className="absolute bottom-24 left-1/2 z-10 flex -translate-x-1/2 items-center gap-4">
          <button
            type="button"
            onClick={() => onToggleLike(post.id, !post.liked)}
            className="flex h-14 w-14 items-center justify-center rounded-full border-2 border-black bg-white text-2xl shadow-lg transition-transform hover:scale-110"
            aria-pressed={post.liked}
            aria-label={post.liked ? "Unlike post" : "Like post"}
          >
            {post.liked ? "❤️" : "🤍"}
          </button>
          <div className="text-sm font-semibold" aria-live="polite">
            {(post.likeCount ?? 0).toLocaleString()} likes
          </div>
          <button
            type="button"
            onClick={() => scrollToPanel(2)}
            className="flex h-14 w-14 items-center justify-center rounded-full border-2 border-black bg-white text-2xl shadow-lg transition-transform hover:scale-110"
            aria-label="Jump to comments panel"
          >
            💬
          </button>
        </div>

        <div className="absolute bottom-6 left-1/2 z-10 flex -translate-x-1/2 gap-2">
          {[0, 1, 2].map((idx) => (
            <div
              key={idx}
              className={`h-2 w-2 rounded-full transition-colors ${
                currentPanel === idx ? "bg-black" : "bg-gray-300"
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

// Main RepDeck Component
export default function RepDeck({ posts = MOCK_POSTS, onToggleLike }: Props) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key.toLowerCase() === "l") e.preventDefault()
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [])

  const handleToggleLike = useCallback(
    (id: Post["id"], liked: boolean) => {
      onToggleLike?.(id, liked)
    },
    [onToggleLike],
  )

  const data = posts ?? MOCK_POSTS

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
        {data.map((post) => (
          <PostCard key={post.id} post={post} onToggleLike={handleToggleLike} />
        ))}
      </div>
    </>
  )
}


// END: REPDECK_COMPONENT