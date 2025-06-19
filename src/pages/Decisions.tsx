
import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import DecisionCardView from "@/components/dashboard/DecisionCardView";
import DecisionTableView from "@/components/dashboard/DecisionTableView";
import DecisionDetail from "@/components/dashboard/DecisionDetail";
import { sampleDecisions } from "@/components/dashboard/data/sampleDecisions";
import { DecisionData } from "@/components/dashboard/types/decision";

const Decisions = () => {
  const [selectedDecision, setSelectedDecision] = useState<DecisionData | null>(null);
  const [viewMode, setViewMode] = useState<"cards" | "table">("cards");
  const [searchTerm, setSearchTerm] = useState("");
  
  // Filter decisions based on search term
  const filteredDecisions = sampleDecisions.filter(decision =>
    decision.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    decision.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    decision.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto">
      <header className="mb-8">
        <h1 className="text-3xl font-bold mb-2">מבט מאקרו</h1>
        <p className="text-gray-600">צפייה וניתוח של החלטות ממשלה</p>
      </header>

      <Card className="mb-8">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm text-gray-500 block mb-1">חיפוש</label>
              <Input 
                placeholder="חיפוש לפי כותרת, תיאור או קטגוריה..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm text-gray-500 block mb-1">סינון לפי קטגוריה</label>
              <select className="w-full p-2 border rounded-md">
                <option>כל הקטגוריות</option>
                <option>חינוך</option>
                <option>בריאות</option>
                <option>כלכלה</option>
                <option>תחבורה</option>
                <option>דיור</option>
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-500 block mb-1">מיון לפי</label>
              <select className="w-full p-2 border rounded-md">
                <option>תאריך - מהחדש לישן</option>
                <option>תאריך - מהישן לחדש</option>
                <option>סיכויי יישום - מהגבוה לנמוך</option>
                <option>סיכויי יישום - מהנמוך לגבוה</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">החלטות ממשלה</h2>
          <div className="flex gap-2 justify-center">
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

        <Tabs defaultValue="all" className="mb-6">
          <TabsList>
            <TabsTrigger value="all">כל ההחלטות</TabsTrigger>
            <TabsTrigger value="education">חינוך</TabsTrigger>
            <TabsTrigger value="health">בריאות</TabsTrigger>
            <TabsTrigger value="economy">כלכלה</TabsTrigger>
            <TabsTrigger value="transportation">תחבורה</TabsTrigger>
          </TabsList>
          
          <TabsContent value="all" className="mt-4">
            {viewMode === "cards" ? (
              <DecisionCardView 
                decisions={filteredDecisions} 
                onSelectDecision={setSelectedDecision} 
              />
            ) : (
              <DecisionTableView 
                decisions={filteredDecisions} 
                onSelectDecision={setSelectedDecision} 
              />
            )}
          </TabsContent>
          
          {/* Other tab contents would filter by category */}
          <TabsContent value="education" className="mt-4">
            {viewMode === "cards" ? (
              <DecisionCardView 
                decisions={filteredDecisions.filter(d => d.category === "חינוך")} 
                onSelectDecision={setSelectedDecision} 
              />
            ) : (
              <DecisionTableView 
                decisions={filteredDecisions.filter(d => d.category === "חינוך")} 
                onSelectDecision={setSelectedDecision} 
              />
            )}
          </TabsContent>
          
          {/* Similar structure for other tabs */}
        </Tabs>
      </div>

      {selectedDecision && (
        <DecisionDetail 
          decision={selectedDecision} 
          onClose={() => setSelectedDecision(null)} 
        />
      )}
    </div>
  );
};

export default Decisions;
