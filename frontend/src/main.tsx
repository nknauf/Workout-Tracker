import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import RepDeck from "./RepDeck";

// BEGIN: SOCIAL_ENTRYPOINT

// If you have a Post type in RepDeck, import it; otherwise keep `any`.
type Post = any;

const getCookie = (name: string) =>
  document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)')?.pop() || "";

function App() {
  const [posts, setPosts] = useState<Post[] | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch("/api/posts/", { credentials: "same-origin" });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setPosts(data);
      } catch (err) {
        console.error("Failed to load posts:", err);
        setPosts([]); // fail gracefully
      }
    })();
  }, []);

  const onToggleLike = async (postId: number | string, liked: boolean) => {
    await fetch(`/social/post/${postId}/like/`, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      credentials: "same-origin",
    });
  };

  if (!posts) {
    return <div className="min-h-screen grid place-items-center">Loading…</div>;
  }

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