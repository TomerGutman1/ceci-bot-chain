
import { DecisionData } from "./types/decision";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter,
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { getFeasibilityColor, getProgressColor } from "./utils/colorHelpers";

interface DecisionCardViewProps {
  decisions: DecisionData[];
  onSelectDecision: (decision: DecisionData) => void;
}

const DecisionCardView = ({ decisions, onSelectDecision }: DecisionCardViewProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {decisions.map((decision) => (
        <Card 
          key={decision.id}
          className="cursor-pointer transition-all hover:shadow-md"
          onClick={() => onSelectDecision(decision)}
        >
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">{decision.title}</CardTitle>
            <CardDescription>מס׳ החלטה: {decision.number} | {decision.date}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-gray-600 line-clamp-2">{decision.description}</p>
              
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">סיכויי יישום:</span>
                  <span className={`font-bold ${getFeasibilityColor(decision.feasibilityScore)}`}>
                    {decision.feasibilityScore}%
                  </span>
                </div>
                <Progress 
                  value={decision.feasibilityScore} 
                  className="h-2"
                  indicatorClassName={getProgressColor(decision.feasibilityScore)}
                />
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">סטטוס יישום:</span>
                  <span className="font-bold">
                    {decision.implementationStatus}%
                  </span>
                </div>
                <Progress 
                  value={decision.implementationStatus} 
                  className="h-2"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span className="font-medium">תקציב:</span>
                  <p className="text-gray-600">{decision.budget || "לא מוגדר"}</p>
                </div>
                <div>
                  <span className="font-medium">גורם אחראי:</span>
                  <p className="text-gray-600">{decision.responsibleParty || "לא מוגדר"}</p>
                </div>
              </div>
            </div>
          </CardContent>
          <CardFooter>
            <Button 
              variant="outline" 
              size="sm" 
              className="w-full"
              onClick={(e) => {
                e.stopPropagation();
                onSelectDecision(decision);
              }}
            >
              ניתוח מפורט
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
};

export default DecisionCardView;
