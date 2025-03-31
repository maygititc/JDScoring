// Calculate score distribution
const calculateScoreDistribution = () => {
  const scoreValues = Object.values(questionScores);
  
  return {
    excellent: scoreValues.filter(score => score >= 80).length,
    good: scoreValues.filter(score => score >= 60 && score < 80).length,
    needsImprovement: scoreValues.filter(score => score < 60).length
  };
};

const { excellent, good, needsImprovement } = calculateScoreDistribution(); 