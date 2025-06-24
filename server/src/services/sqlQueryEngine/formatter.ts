/**
 * Response Formatter
 * Formats SQL query results into Hebrew responses
 */

export class ResponseFormatter {
  format(
    result: any, 
    queryType: string,
    originalQuery?: string
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
        return this.formatCount(data);
      
      case 'aggregate':
        return this.formatAggregateStats(data);
      
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

  private formatMultipleDecisions(decisions: any[]): string {
    if (!decisions || decisions.length === 0) {
      return '😔 לא נמצאו החלטות התואמות לבקשה';
    }

    let response = `📊 נמצאו ${decisions.length} החלטות רלוונטיות:\n\n`;

    decisions.slice(0, 10).forEach((decision, index) => {
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

    if (decisions.length > 10) {
      response += `\n... ועוד ${decisions.length - 10} החלטות נוספות\n`;
    }

    response += '\n💡 טיפ: לחץ על קישור או בקש החלטה ספציפית לפרטים מלאים';

    return response;
  }

  private formatCount(data: any): string {
    if (!data || data.length === 0) {
      return '📊 לא נמצאו נתונים';
    }

    const result = data[0];
    const count = result.count || 0;

    // Total count query
    if (!result.year && !result.topic) {
      let response = `📊 במסד הנתונים יש **${count.toLocaleString('he-IL')} החלטות ממשלה**`;
      return response;
    }

    if (result.year) {
      let response = `📊 בשנת ${result.year} התקבלו **${count} החלטות ממשלה**`;
      
      if (result.governments_count) {
        response += `\n🏛️ על ידי ${result.governments_count} ממשלות שונות`;
      }
      
      if (result.topics_count) {
        response += `\n🏷️ ב-${result.topics_count} תחומי מדיניות שונים`;
      }
      
      return response;
    }

    if (result.topic) {
      let response = `📊 נמצאו **${count} החלטות** בנושא ${result.topic}`;
      
      if (result.first_decision && result.last_decision) {
        response += `\n📅 בין התאריכים ${this.formatDate(result.first_decision)} - ${this.formatDate(result.last_decision)}`;
      }
      
      if (result.governments_count) {
        response += `\n🏛️ על ידי ${result.governments_count} ממשלות שונות`;
      }
      
      return response;
    }

    return `📊 נמצאו **${count} החלטות**`;
  }

  private formatAggregateStats(data: any): string {
    if (!data || data.length === 0) {
      return '📊 לא נמצאו נתונים סטטיסטיים';
    }

    const stats = data[0];
    let response = `📊 סטטיסטיקה לממשלה מספר ${stats.government_number}\n\n`;

    if (stats.prime_minister) {
      response += `👤 ראש הממשלה: ${stats.prime_minister}\n`;
    }

    response += `📋 סה"כ החלטות: ${stats.total_decisions}\n`;

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
