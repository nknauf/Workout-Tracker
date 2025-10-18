import React, { useCallback, useMemo, useState } from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import RepDeck, { type Post } from "./RepDeck";

// BEGIN: SOCIAL_ENTRYPOINT

const getCookie = (name: string) =>
  document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)')?.pop() || "";

const loadInitialPosts = (): Post[] => {
  const dataNode = document.getElementById("repdeck-data");
  if (!dataNode || !dataNode.textContent) {
    return [];
  }
  try {
    return JSON.parse(dataNode.textContent) as Post[];
  } catch (error) {
    console.error("Failed to parse initial posts", error);
    return [];
  }
};

function App() {
  const initialPosts = useMemo(() => loadInitialPosts(), []);
  const [posts, setPosts] = useState<Post[]>(initialPosts);

  const onToggleLike = useCallback(
    async (postId: Post["id"], liked: boolean) => {
      let previous: { liked: boolean; likeCount: number } | null = null;
      setPosts((current) =>
        current.map((post) => {
          if (post.id !== postId) return post;
          previous = { liked: !!post.liked, likeCount: post.likeCount ?? 0 };
          const nextCount = Math.max(0, (post.likeCount ?? 0) + (liked ? 1 : -1));
          return { ...post, liked, likeCount: nextCount };
        }),
      );

      try {
        const response = await fetch(`/social/post/${postId}/like/`, {
          method: "POST",
          headers: { "X-CSRFToken": getCookie("csrftoken") },
          credentials: "same-origin",
        });
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const payload = await response.json();
        setPosts((current) =>
          current.map((post) =>
            post.id === postId
              ? { ...post, liked: payload.liked, likeCount: payload.count }
              : post,
          ),
        );
      } catch (error) {
        console.error("Failed to toggle like", error);
        if (previous) {
          const { liked: prevLiked, likeCount: prevCount } = previous;
          setPosts((current) =>
            current.map((post) =>
              post.id === postId ? { ...post, liked: prevLiked, likeCount: prevCount } : post,
            ),
          );
        }
      }
    },
    [],
  );

  return (
    <div className="min-h-screen bg-white text-black">
      <RepDeck posts={posts} onToggleLike={onToggleLike} />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("repdeck-root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// END: SOCIAL_ENTRYPOINT