
export const getFeasibilityColor = (score: number) => {
  if (score >= 75) return "text-green-600";
  if (score >= 50) return "text-amber-600";
  return "text-red-600";
};

export const getProgressColor = (score: number) => {
  if (score >= 75) return "bg-green-600";
  if (score >= 50) return "bg-amber-600";
  return "bg-red-600";
};
