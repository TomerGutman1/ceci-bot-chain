
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { sampleDecisions } from "./data/sampleDecisions";
import { DecisionData } from "./types/decision";
import DecisionCardView from "./DecisionCardView";
import DecisionTableView from "./DecisionTableView";
import DecisionDetail from "./DecisionDetail";

const DecisionAnalysis = () => {
  const [selectedDecision, setSelectedDecision] = useState<DecisionData | null>(null);
  const [viewMode, setViewMode] = useState<"cards" | "table">("cards");

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-4">
        <div className="flex gap-2">
          <Button
            variant={viewMode === "cards" ? "default" : "outline"}
            size="sm"
            onClick={() => setViewMode("cards")}
          >
            תצוגת כרטיסיות
          </Button>
          <Button
            variant={viewMode === "table" ? "default" : "outline"}
            size="sm"
            onClick={() => setViewMode("table")}
          >
            תצוגת טבלה
          </Button>
        </div>
      </div>

      {viewMode === "cards" ? (
        <DecisionCardView 
          decisions={sampleDecisions} 
          onSelectDecision={setSelectedDecision} 
        />
      ) : (
        <DecisionTableView 
          decisions={sampleDecisions} 
          onSelectDecision={setSelectedDecision} 
        />
      )}

      {selectedDecision && (
        <DecisionDetail 
          decision={selectedDecision} 
          onClose={() => setSelectedDecision(null)} 
        />
      )}
    </div>
  );
};

export default DecisionAnalysis;
