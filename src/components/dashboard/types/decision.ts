
export interface DecisionData {
  id: string;
  title: string;
  number: string;
  date: string;
  category: string;
  feasibilityScore: number;
  implementationStatus: number;
  strengths: string[];
  weaknesses: string[];
  budget?: string;
  responsibleParty?: string;
  timeline?: string;
  relatedDecisions?: string[];
  description?: string;
}
