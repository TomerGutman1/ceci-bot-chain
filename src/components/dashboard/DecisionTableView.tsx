
import { DecisionData } from "./types/decision";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { getFeasibilityColor } from "./utils/colorHelpers";

interface DecisionTableViewProps {
  decisions: DecisionData[];
  onSelectDecision: (decision: DecisionData) => void;
}

const DecisionTableView = ({ decisions, onSelectDecision }: DecisionTableViewProps) => {
  return (
    <Card className="shadow-sm">
      <CardContent className="p-0 overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>מס׳ החלטה</TableHead>
              <TableHead>כותרת</TableHead>
              <TableHead>תאריך</TableHead>
              <TableHead>תחום</TableHead>
              <TableHead>סיכויי יישום</TableHead>
              <TableHead>סטטוס נוכחי</TableHead>
              <TableHead>פעולות</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {decisions.map((decision) => (
              <TableRow 
                key={decision.id} 
                className="cursor-pointer" 
                onClick={() => onSelectDecision(decision)}
              >
                <TableCell>{decision.number}</TableCell>
                <TableCell>{decision.title}</TableCell>
                <TableCell>{decision.date}</TableCell>
                <TableCell>{decision.category}</TableCell>
                <TableCell>
                  <span className={`font-bold ${getFeasibilityColor(decision.feasibilityScore)}`}>
                    {decision.feasibilityScore}%
                  </span>
                </TableCell>
                <TableCell>{decision.implementationStatus}%</TableCell>
                <TableCell>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectDecision(decision);
                    }}
                  >
                    פרטים
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
};

export default DecisionTableView;
