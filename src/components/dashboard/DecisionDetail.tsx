
import { DecisionData } from "./types/decision";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getFeasibilityColor, getProgressColor } from "./utils/colorHelpers";

interface DecisionDetailProps {
  decision: DecisionData;
  onClose: () => void;
}

const DecisionDetail = ({ decision, onClose }: DecisionDetailProps) => {
  return (
    <Card className="shadow-sm mt-6">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>ניתוח מפורט - {decision.title}</CardTitle>
          <CardDescription>
            מס׳ החלטה: {decision.number} | תאריך: {decision.date} | תחום: {decision.category}
          </CardDescription>
        </div>
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={onClose}
        >
          סגור
        </Button>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="summary">
          <TabsList className="grid grid-cols-4 mb-4">
            <TabsTrigger value="summary">סיכום</TabsTrigger>
            <TabsTrigger value="details">פרטים מלאים</TabsTrigger>
            <TabsTrigger value="factors">גורמים משפיעים</TabsTrigger>
            <TabsTrigger value="recommendations">המלצות</TabsTrigger>
          </TabsList>
          
          <TabsContent value="summary" className="space-y-6">
            <div>
              <p className="mb-4">{decision.description}</p>
            </div>
          
            <div>
              <h4 className="font-medium mb-2">סיכויי יישום</h4>
              <div className="flex items-center gap-4">
                <Progress 
                  value={decision.feasibilityScore} 
                  className="h-3 flex-1"
                  indicatorClassName={getProgressColor(decision.feasibilityScore)}
                />
                <span className={`text-xl font-bold ${getFeasibilityColor(decision.feasibilityScore)}`}>
                  {decision.feasibilityScore}%
                </span>
              </div>
            </div>

            <div>
              <h4 className="font-medium mb-2">סטטוס יישום נוכחי</h4>
              <div className="flex items-center gap-4">
                <Progress 
                  value={decision.implementationStatus} 
                  className="h-3 flex-1"
                />
                <span className="text-xl font-bold">
                  {decision.implementationStatus}%
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-2 text-green-600">חוזקות</h4>
                <ul className="list-disc list-inside space-y-1">
                  {decision.strengths.map((strength, index) => (
                    <li key={index} className="text-sm">{strength}</li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium mb-2 text-red-600">חולשות</h4>
                <ul className="list-disc list-inside space-y-1">
                  {decision.weaknesses.map((weakness, index) => (
                    <li key={index} className="text-sm">{weakness}</li>
                  ))}
                </ul>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="details" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-1">תקציב</h4>
                  <p>{decision.budget || "לא מוגדר"}</p>
                </div>
                
                <div>
                  <h4 className="font-medium mb-1">גורם אחראי</h4>
                  <p>{decision.responsibleParty || "לא מוגדר"}</p>
                </div>
                
                <div>
                  <h4 className="font-medium mb-1">לוח זמנים</h4>
                  <p>{decision.timeline || "לא מוגדר"}</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-1">החלטות קשורות</h4>
                  {decision.relatedDecisions && decision.relatedDecisions.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {decision.relatedDecisions.map((decisionId) => (
                        <Button key={decisionId} variant="outline" size="sm">
                          החלטה {decisionId}
                        </Button>
                      ))}
                    </div>
                  ) : (
                    <p>אין החלטות קשורות</p>
                  )}
                </div>
                
                <div>
                  <h4 className="font-medium mb-1">תיאור מלא</h4>
                  <p>{decision.description}</p>
                </div>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="factors" className="py-4">
            <div className="space-y-4">
              <p>הגורמים המשפיעים ביותר על סיכויי היישום של החלטה זו:</p>
              
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium">תקציב מספק</span>
                    <span className="text-sm font-medium">גבוה</span>
                  </div>
                  <Progress value={85} className="h-2" />
                </div>
                
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium">הגדרת גורם אחראי</span>
                    <span className="text-sm font-medium">בינוני-גבוה</span>
                  </div>
                  <Progress value={70} className="h-2" />
                </div>
                
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium">לוח זמנים ריאלי</span>
                    <span className="text-sm font-medium">בינוני</span>
                  </div>
                  <Progress value={60} className="h-2" />
                </div>
                
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium">מורכבות בירוקרטית</span>
                    <span className="text-sm font-medium">בינוני-נמוך</span>
                  </div>
                  <Progress value={40} className="h-2" />
                </div>
                
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium">תמיכה פוליטית</span>
                    <span className="text-sm font-medium">נמוך</span>
                  </div>
                  <Progress value={25} className="h-2" />
                </div>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="recommendations" className="py-4">
            <div className="space-y-4">
              <p className="font-medium">להגברת סיכויי היישום של החלטה זו, מומלץ:</p>
              
              <ul className="list-decimal list-inside space-y-2 mr-4">
                <li>הגדרת מדדי הצלחה ברורים ומדידים</li>
                <li>הקצאת משאבים נוספים לגורם המיישם</li>
                <li>פישוט תהליכים בירוקרטיים הקשורים ליישום</li>
                <li>שיפור התיאום הבין-משרדי</li>
                <li>קביעת נקודות בקרה תקופתיות לבחינת התקדמות</li>
              </ul>
              
              <div className="mt-6">
                <Button className="bg-ceci-blue hover:bg-blue-700">
                  צור דוח המלצות מפורט
                </Button>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default DecisionDetail;
