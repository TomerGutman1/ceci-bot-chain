/**
 * Response Formatter
 * Formats SQL query results into Hebrew responses
 */

export class ResponseFormatter {
  format(
    result: any, 
    queryType: string,
    originalQuery?: string,
    metadata?: any
  ): string {
    if (!result.success) {
      return this.formatError(result.error);
    }

    const data = result.data;
    
    if (!data || (Array.isArray(data) && data.length === 0)) {
      return this.formatNoResults(originalQuery);
    }

    switch (queryType) {
      case 'single':
        return this.formatSingleDecision(data[0]);
      
      case 'multiple':
        return this.formatMultipleDecisions(data);
      
      case 'count':
        return this.formatCount(data, originalQuery, metadata);
      
      case 'aggregate':
        return this.formatAggregateStats(data, originalQuery);
      
      default:
        return this.formatGeneric(data);
    }
  }

  private formatError(error: string): string {
    return `❌ שגיאה בביצוע השאילתה: ${error}`;
  }

  private formatNoResults(query?: string): string {
    if (query && query.includes('החלטה')) {
      return '😔 לא נמצאה החלטה התואמת לבקשה';
    }
    return '😔 לא נמצאו תוצאות התואמות לבקשה';
  }

  private formatSingleDecision(decision: any): string {
    if (!decision) {
      return '😔 לא נמצאה החלטה התואמת לבקשה';
    }

    let response = `🏛️ החלטת ממשלה מס' ${decision.decision_number}\n\n`;

    // Title
    if (decision.decision_title && decision.decision_title !== 'null') {
      response += `📋 ${decision.decision_title}\n\n`;
    }

    // Basic details
    response += `🔢 מספר החלטה: ${decision.decision_number}\n`;
    response += `🏢 ממשלה מספר: ${decision.government_number}\n`;
    response += `📅 תאריך: ${this.formatDate(decision.decision_date)}\n`;
    
    if (decision.prime_minister) {
      response += `👤 ראש הממשלה: ${decision.prime_minister}\n`;
    }

    // Tags
    if (decision.tags_policy_area) {
      response += `\n🏷️ תחומים: ${decision.tags_policy_area}\n`;
    }

    if (decision.tags_government_body) {
      response += `🏦 גופים מעורבים: ${decision.tags_government_body}\n`;
    }

    // Content
    response += '\n';
    
    if (decision.summary && decision.summary !== 'null') {
      response += '📝 תקציר:\n\n';
      const summary = decision.summary.length > 500 
        ? decision.summary.substring(0, 497) + '...' 
        : decision.summary;
      response += `${summary}\n`;
    } else if (decision.decision_content && decision.decision_content !== 'null') {
      response += '📄 מתוך ההחלטה:\n\n';
      const content = decision.decision_content.length > 500 
        ? decision.decision_content.substring(0, 497) + '...' 
        : decision.decision_content;
      response += `${content}\n`;
    }

    // Operativity
    if (decision.operativity) {
      const emoji = decision.operativity === 'אופרטיבי' ? '✅' : '📋';
      response += `\n${emoji} סטטוס: ${decision.operativity}\n`;
    }

    // Link
    if (decision.decision_url) {
      response += `\n🔗 קישור להחלטה: ${decision.decision_url}`;
    }

    return response;
  }

  private formatMultipleDecisions(decisions: any): string {
    // Ensure decisions is an array
    const decisionsArray = Array.isArray(decisions) ? decisions : [decisions];
    
    if (!decisionsArray || decisionsArray.length === 0) {
      return '😔 לא נמצאו החלטות התואמות לבקשה';
    }

    // If only one decision, format as single
    if (decisionsArray.length === 1) {
      return this.formatSingleDecision(decisionsArray[0]);
    }

    let response = `📊 נמצאו ${decisionsArray.length} החלטות רלוונטיות:\n\n`;

    // Show all decisions if 20 or less, otherwise limit to 20
    const maxToShow = Math.min(decisionsArray.length, 20);
    decisionsArray.slice(0, maxToShow).forEach((decision, index) => {
      response += `**${index + 1}. החלטה מס' ${decision.decision_number}**\n`;
      
      if (decision.decision_title && decision.decision_title !== 'null') {
        response += `📋 ${decision.decision_title}\n`;
      }
      
      response += `📅 תאריך: ${this.formatDate(decision.decision_date)}\n`;
      response += `🏢 ממשלה מספר: ${decision.government_number}\n`;
      
      if (decision.tags_policy_area) {
        response += `🏷️ תחומים: ${decision.tags_policy_area}\n`;
      }
      
      if (decision.summary && decision.summary !== 'null') {
        const shortSummary = decision.summary.length > 150 
          ? decision.summary.substring(0, 147) + '...' 
          : decision.summary;
        response += `📝 תקציר: ${shortSummary}\n`;
      }
      
      if (decision.decision_url) {
        response += `🔗 קישור: ${decision.decision_url}\n`;
      }
      
      response += '\n' + '─'.repeat(50) + '\n\n';
    });

    if (decisionsArray.length > maxToShow) {
      response += `\n... ועוד ${decisionsArray.length - maxToShow} החלטות נוספות\n`;
    }

    response += '\n💡 טיפ: לחץ על קישור או בקש החלטה ספציפית לפרטים מלאים';

    return response;
  }

  private formatCount(data: any, originalQuery?: string, metadata?: any): string {
    if (!data) {
      return '📊 לא נמצאו נתונים';
    }

    // Handle both array and object responses
    const result = Array.isArray(data) ? data[0] : data;
    
    if (!result) {
      return '📊 לא נמצאו נתונים';
    }
    
    const count = result.count || 0;

    // Extract context from the original query
    if (originalQuery) {
      // Check for government number
      const govMatch = originalQuery.match(/ממשלה\s+(?:מס(?:פר)?\s*)?(\d+)/);
      const governmentNumber = govMatch ? govMatch[1] : null;
      
      // Check for topic
      const topicMatch = originalQuery.match(/בנושא\s+([\u0590-\u05FF\s]+?)(?:\s|\?|$)/);
      const topic = topicMatch ? topicMatch[1].trim() : null;
      
      // Check for year
      const yearMatch = originalQuery.match(/(?:ב|מ)?שנת\s+(\d{4})/);
      const year = yearMatch ? yearMatch[1] : null;
      
      // Check for operativity type
      const operativityMatch = originalQuery.match(/החלטות\s+(דקלרטיביות|אופרטיביות)/);
      const operativityType = operativityMatch ? operativityMatch[1] : null;
      
      // Check for date range
      const dateRangeMatch = originalQuery.match(/בין\s+(\d{4})\s+(?:ל|עד)\s*(\d{4})/);
      const startYear = dateRangeMatch ? dateRangeMatch[1] : null;
      const endYear = dateRangeMatch ? dateRangeMatch[2] : null;
      
      // Check for prime minister
      const pmMatch = originalQuery.match(/(?:קיבל|החליט|עשה)\s+([\u0590-\u05FF\s]+?)\s+בנושא/);
      const primeMinister = pmMatch ? pmMatch[1].trim() : null;
      
      // Build specific response based on query context
      if (governmentNumber && topic) {
        return `📊 ממשלה ${governmentNumber} קיבלה **${count.toLocaleString('he-IL')} החלטות** בנושא ${topic}`;
      }
      
      if (governmentNumber && !topic) {
        return `📊 ממשלה ${governmentNumber} קיבלה **${count.toLocaleString('he-IL')} החלטות** בסך הכל`;
      }
      
      if (topic && startYear && endYear) {
        return `📊 נמצאו **${count.toLocaleString('he-IL')} החלטות** בנושא ${topic} בין השנים ${startYear}-${endYear}`;
      }
      
      if (topic && year) {
        return `📊 בשנת ${year} התקבלו **${count.toLocaleString('he-IL')} החלטות** בנושא ${topic}`;
      }
      
      if (topic && !year && !governmentNumber) {
        return `📊 נמצאו **${count.toLocaleString('he-IL')} החלטות** בנושא ${topic}`;
      }
      
      if (year && !topic) {
        return `📊 בשנת ${year} התקבלו **${count.toLocaleString('he-IL')} החלטות ממשלה**`;
      }
      
      if (operativityType && year) {
        return `📊 בשנת ${year} היו **${count.toLocaleString('he-IL')} החלטות ${operativityType}**`;
      }
      
      if (operativityType && !year) {
        return `📊 נמצאו **${count.toLocaleString('he-IL')} החלטות ${operativityType}** בסך הכל`;
      }
      
      if (primeMinister && topic) {
        return `📊 ${primeMinister} קיבל **${count.toLocaleString('he-IL')} החלטות** בנושא ${topic}`;
      }
      
      // Check for "כל הממשלות"
      if (originalQuery.includes('כל ממשלה')) {
        return `📊 סטטיסטיקת החלטות לפי ממשלה:\n\n${this.formatGovernmentStats(data)}`;
      }
    }

    // Count with topic and date range from result data
    if (result.topic && result.start_year && result.end_year) {
      let response = `📊 נמצאו **${count.toLocaleString('he-IL')} החלטות** בנושא **${result.topic}**`;
      response += `\n📅 בין השנים ${result.start_year}-${result.end_year}`;
      
      if (result.first_decision && result.last_decision && count > 0) {
        response += `\n⏮️ ההחלטה הראשונה: ${this.formatDate(result.first_decision)}`;
        response += `\n⏭️ ההחלטה האחרונה: ${this.formatDate(result.last_decision)}`;
      }
      
      if (result.governments_count) {
        response += `\n🏛️ על ידי ${result.governments_count} ממשלות שונות`;
      }
      
      return response;
    }

    // Total count query
    if (!result.year && !result.topic && originalQuery && (originalQuery.includes('בסך הכל') || originalQuery.includes('כמה החלטות יש'))) {
      return `📊 במסד הנתונים יש **${count.toLocaleString('he-IL')} החלטות ממשלה** בסך הכל`;
    }

    // Fallback to generic count
    return `📊 נמצאו **${count.toLocaleString('he-IL')} החלטות**`;
  }

  private formatAggregateStats(data: any, originalQuery?: string): string {
    if (!data) {
      return '📊 לא נמצאו נתונים סטטיסטיים';
    }

    // Check if this is monthly trend data
    if (Array.isArray(data) && data.length > 0 && data[0].month !== undefined) {
      return this.formatMonthlyTrend(data, originalQuery);
    }

    // Check if this is government statistics
    if (Array.isArray(data) && data.length > 0 && data[0].government_number !== undefined && data[0].count !== undefined) {
      return this.formatGovernmentStats(data);
    }

    const stats = Array.isArray(data) ? data[0] : data;
    
    if (!stats) {
      return '📊 לא נמצאו נתונים סטטיסטיים';
    }
    
    let response = `📊 סטטיסטיקה לממשלה מספר ${stats.government_number}\n\n`;

    if (stats.prime_minister) {
      response += `👤 ראש הממשלה: ${stats.prime_minister}\n`;
    }

    response += `📋 סה"כ החלטות: ${stats.total_decisions || stats.decision_count || stats.count || 0}\n`;

    if (stats.first_decision && stats.last_decision) {
      response += `📅 תקופת כהונה: ${this.formatDate(stats.first_decision)} - ${this.formatDate(stats.last_decision)}\n`;
      
      // Calculate duration
      const start = new Date(stats.first_decision);
      const end = new Date(stats.last_decision);
      const durationDays = Math.floor((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
      response += `⏱️ משך: ${durationDays} ימים\n`;
    }

    if (stats.policy_areas && Array.isArray(stats.policy_areas)) {
      response += `\n🏷️ תחומי מדיניות עיקריים:\n`;
      stats.policy_areas.slice(0, 10).forEach((area: string) => {
        response += `  • ${area}\n`;
      });
    }

    return response;
  }

  private formatGeneric(data: any): string {
    if (Array.isArray(data)) {
      return `📊 נמצאו ${data.length} תוצאות`;
    }
    
    return `📊 תוצאה:\n${JSON.stringify(data, null, 2)}`;
  }

  private formatDate(dateStr: string): string {
    if (!dateStr) return 'לא צוין';
    
    try {
      const date = new Date(dateStr);
      
      const hebrewMonths = {
        0: 'ינואר', 1: 'פברואר', 2: 'מרץ', 3: 'אפריל',
        4: 'מאי', 5: 'יוני', 6: 'יולי', 7: 'אוגוסט',
        8: 'ספטמבר', 9: 'אוקטובר', 10: 'נובמבר', 11: 'דצמבר'
      };
      
      const day = date.getDate();
      const month = hebrewMonths[date.getMonth() as keyof typeof hebrewMonths];
      const year = date.getFullYear();
      
      return `${day} ב${month} ${year}`;
    } catch {
      return dateStr;
    }
  }

  private formatGovernmentStats(data: any[]): string {
    let response = '📊 סטטיסטיקת החלטות לפי ממשלה:\n\n';
    data.forEach((gov: any, index: number) => {
      response += `${index + 1}. ממשלה ${gov.government_number}: ${gov.count} החלטות`;
      if (gov.prime_minister) {
        response += ` (${gov.prime_minister})`;
      }
      response += '\n';
    });
    return response;
  }

  private formatMonthlyTrend(data: any[], originalQuery?: string): string {
    const hebrewMonths = [
      'ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני',
      'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר'
    ];
    
    // Extract year from query
    let year = '';
    if (originalQuery) {
      const yearMatch = originalQuery.match(/ב[-\s]?(\d{4})/);
      if (yearMatch) {
        year = yearMatch[1];
      }
    }
    
    let response = `📊 התפלגות החלטות לפי חודש${year ? ` בשנת ${year}` : ''}:\n\n`;
    
    // Calculate total
    const total = data.reduce((sum, month) => sum + (month.count || 0), 0);
    
    // Sort by month number
    const sortedData = [...data].sort((a, b) => a.month - b.month);
    
    sortedData.forEach((monthData) => {
      const monthName = hebrewMonths[monthData.month - 1] || `חודש ${monthData.month}`;
      const count = monthData.count || 0;
      const percentage = total > 0 ? ((count / total) * 100).toFixed(1) : '0';
      
      // Create a simple bar chart
      const barLength = Math.round((count / Math.max(...data.map(m => m.count))) * 20);
      const bar = '█'.repeat(barLength || 1);
      
      response += `${monthName}: ${count} החלטות (${percentage}%) ${bar}\n`;
    });
    
    response += `\n📋 סה"כ: ${total} החלטות`;
    
    return response;
  }

  // Helper method to format for specific use cases
  formatNotFound(
    decisionNumber: string, 
    governmentNumber: number,
    otherGovernments?: number[]
  ): string {
    let response = `😔 לא נמצאה החלטה ${decisionNumber} בממשלה ${governmentNumber}`;
    
    if (otherGovernments && otherGovernments.length > 0) {
      response += `\n\n💡 ההחלטה קיימת בממשלות: ${otherGovernments.join(', ')}`;
      response += `\nנסה: "החלטה ${decisionNumber} של ממשלה ${otherGovernments[0]}"`;
    }
    
    return response;
  }
}
