/**
 * Chart utility functions for EProfile component
 * Handles data processing and transformation for activity charts
 */

/**
 * Processes raw activity data from API into chart-ready format
 * @param {Array} totalCountArray - Array of [dateString, count] pairs from API
 * @returns {Object} { labels: Array, values: Array }
 */
export function processActivityData(totalCountArray) {
  const labels = []
  const values = []
  
  // Sort the data by date first to ensure chronological order
  const sortedData = [...totalCountArray].sort((a, b) => {
    if (Array.isArray(a) && Array.isArray(b) && a.length >= 2 && b.length >= 2) {
      return new Date(a[0]) - new Date(b[0])
    }
    return 0
  })
  
  // Process each array in total_count
  sortedData.forEach(dataPoint => {
    if (Array.isArray(dataPoint) && dataPoint.length >= 2) {
      const dateString = dataPoint[0] // e.g., "2024-08"
      const commitCount = dataPoint[1] // e.g., 11
      
      // Convert date string to Korean month format
      const monthLabel = convertDateToKoreanMonth(dateString)
      
      labels.push(monthLabel)
      values.push(commitCount)
    }
  })
  
  return { labels, values }
}

/**
 * Converts date string to Korean month format
 * @param {string} dateString - Date in "YYYY-MM" format
 * @returns {string} Korean month format like "6월"
 */
export function convertDateToKoreanMonth(dateString) {
  try {
    // dateString format: "2024-08" or "2025-06"
    const [year, month] = dateString.split('-')
    const monthNumber = parseInt(month, 10)
    
    const monthNames = {
      1: '1월', 2: '2월', 3: '3월', 4: '4월',
      5: '5월', 6: '6월', 7: '7월', 8: '8월', 
      9: '9월', 10: '10월', 11: '11월', 12: '12월'
    }
    
    return monthNames[monthNumber] || `${monthNumber}월`
  } catch (error) {
    console.error('Date conversion error:', error, dateString)
    return dateString // Return original if conversion fails
  }
}

/**
 * Estimates commit lines based on commit count
 * @param {number} commitCount - Number of commits
 * @param {number} multiplier - Lines per commit estimate (default: 8.5)
 * @returns {number} Estimated lines of code
 */
export function estimateCommitLines(commitCount, multiplier = 8.5) {
  return Math.round(commitCount * multiplier)
}

export function processAddedLinesData(addedLinesArray) {
  const labels = []
  const values = []
  
  // Sort the data by date first to ensure chronological order
  const sortedData = [...addedLinesArray].sort((a, b) => {
    if (Array.isArray(a) && Array.isArray(b) && a.length >= 2 && b.length >= 2) {
      return new Date(a[0]) - new Date(b[0])
    }
    return 0
  })
  
  // Process each array in added_lines
  sortedData.forEach(dataPoint => {
    if (Array.isArray(dataPoint) && dataPoint.length >= 2) {
      const dateString = dataPoint[0] // e.g., "2024-08"
      const lineCount = dataPoint[1] // e.g., 1836
      
      // Convert date string to Korean month format
      const monthLabel = convertDateToKoreanMonth(dateString)
      
      labels.push(monthLabel)
      values.push(lineCount)
    }
  })
  
  return { labels, values }
}