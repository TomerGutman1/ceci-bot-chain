
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent } from "@/components/ui/card";
import DecisionAnalysis from "@/components/dashboard/DecisionAnalysis";
import ChatInterface from "@/components/chat/ChatInterface";

const Dashboard = () => {
  return (
    <div className="container mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">שלום, משתמש</h1>
        <p className="text-ceci-gray">ברוכים הבאים למערכת ניתוח והערכת החלטות ממשלה</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {[
          { title: "החלטות שנותחו", value: "124", change: "+12%" },
          { title: "ממוצע סיכויי יישום", value: "63%", change: "+2%" },
          { title: "דוחות שהופקו", value: "38", change: "+5" },
        ].map((stat, idx) => (
          <Card key={idx}>
            <CardContent className="p-6">
              <p className="text-sm text-ceci-gray">{stat.title}</p>
              <div className="flex items-center justify-between">
                <p className="text-3xl font-bold">{stat.value}</p>
                <span className="text-sm text-green-600">{stat.change}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Tabs defaultValue="decisions" className="space-y-6">
        <TabsList className="grid grid-cols-2 md:w-[400px]">
          <TabsTrigger value="decisions">החלטות וניתוחים</TabsTrigger>
          <TabsTrigger value="assistant">עוזר AI</TabsTrigger>
        </TabsList>
        
        <TabsContent value="decisions" className="space-y-6">
          <Card>
            <CardContent className="p-6">
              <div className="mb-6 flex justify-between items-center">
                <h2 className="text-xl font-bold">ניתוחי החלטות אחרונים</h2>
                <input
                  type="search"
                  placeholder="חיפוש החלטות..."
                  className="px-4 py-2 border border-gray-200 rounded-md max-w-sm"
                />
              </div>
              <DecisionAnalysis />
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="assistant">
          <Card>
            <CardContent className="p-6">
              <div className="mb-6">
                <h2 className="text-xl font-bold mb-2">עוזר ה-AI של CECI</h2>
                <p className="text-ceci-gray">
                  שאל שאלות על החלטות ממשלה, מדיניות ציבורית או קבל ניתוחים וחיזויים בזמן אמת
                </p>
              </div>
              <ChatInterface />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Dashboard;
