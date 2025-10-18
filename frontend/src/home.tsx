
import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";

// BEGIN: HOME_ENTRYPOINT

type MacroTot = { calories: number; protein: number; carbs: number; fats: number };
type WorkoutCard = { id: string|number; title: string; items: Array<{ name: string; sets?: number; reps?: string }> };
type MealCard = { id: string|number; name: string; macros: MacroTot; photoUrl?: string };
type PumpPic = { id: string|number; url: string; alt?: string };

type HomeProps = {
  todayWorkouts: WorkoutCard[];
  todayMeals: MealCard[];
  todayTotals: MacroTot;
  pumpPics: PumpPic[];
  onOpenAgent?: () => void;
};

function HomeDashboard(props: HomeProps) {
  return (
    <div className="min-h-screen bg-white text-black p-4">
      <h1 className="text-2xl font-bold mb-4">Today</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-md border border-black p-4">Workouts bubble</div>
        <div className="rounded-md border border-black p-4">Meals bubble</div>
        <div className="rounded-md border border-black p-4">Totals bubble</div>
        <div className="rounded-md border border-black p-4">Pump Pics bubble</div>
      </div>
      <div className="mt-6 rounded-md border border-black p-4">
        <div className="font-semibold mb-2">Chatbot</div>
        <button className="border border-black rounded px-3 py-2" onClick={props.onOpenAgent}>
          Open Agent
        </button>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("home-root")!).render(
  <React.StrictMode>
    <HomeDashboard
      todayWorkouts={[]}
      todayMeals={[]}
      todayTotals={{ calories: 0, protein: 0, carbs: 0, fats: 0 }}
      pumpPics={[]}
    />
  </React.StrictMode>
);

// END: HOME_ENTRYPOINT