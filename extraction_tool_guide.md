# 📖 Wikipedia Extraction Manager / 위키백과 추출 관리자

---

## 🛠️ Overview

Wikipedia Extraction Manager is a desktop tool for extracting structured data (events, people, metadata) from Wikipedia, starting from a user-defined event page. The tool supports both English and Korean, and outputs data to a CSV file and/or a local database.

---

## 🔍 Data Extraction Mechanism

1. **Seed Event** 🌱
   - The extraction process begins from a user-specified Wikipedia event page (the “Seed URL”).
   - Example: `https://en.wikipedia.org/wiki/Korean_War`

2. **Traversal Logic** 🔗
   - The tool alternates between extracting people from events and events from people, up to a user-defined “Max Degree” of separation.
   - **Degree 0:** Seed event  
   - **Degree 1:** People from the event (from “Commanders and leaders” in the infobox)  
   - **Degree 2:** Events from those people (from “Battles/wars” in the infobox)  
   - **Degree 3:** People from those events, etc.

3. **Data Collected for Each Node** 📦
   - **node_id:** Unique identifier (e.g., e1, p1, etc.)
   - **node_type:** “Event” or “Person”
   - **name:** Name of the event or person
   - **description:** Description from the infobox
   - **start_date / end_date:** Extracted from infobox if available
   - **metadata:** Additional structured data from the infobox (as JSON)
   - **parent_url:** The Wikipedia page from which this node was discovered

4. **Output** 💾
   - All extracted data is saved to `data/Nodes.csv` (CSV file) and/or `data/wikipedia_extraction.db` (SQLite database), located in the `data` folder next to the application.

---

## ⚙️ Tool Options

- **Output Type:**
  - **SQL Database / SQL 데이터베이스:** Save data to a local SQLite database.
  - **CSV File / CSV 파일:** Save data to a CSV file.

- **Seed URL / 시작 URL:**
  - The starting Wikipedia page for extraction.

- **Max Degree / 최대 단계:**
  - The number of “hops” from the seed event to traverse (higher values extract more data, but take longer).

- **Start Extraction / 추출 시작:**
  - Begins the extraction process.

- **Stop / 중지:**
  - Stops the extraction and saves all data collected so far.

- **Log / Status / 로그 / 상태:**
  - Shows real-time progress and any errors.

---

## ⚠️ Important Note on Wikipedia Data Structure

Wikipedia’s infoboxes and page structures are **not always consistent** across different events and people.  
- Some pages may use different section names, formats, or may lack structured infoboxes entirely.
- As a result, the tool may not extract as much data from some events as it does from others.

**Future Improvements:**
- As we enhance the tool, we will implement more robust and flexible extraction logic, including fallback mechanisms to handle these inconsistencies.
- This may include:
  - Recognizing alternative infobox field names
  - Using additional heuristics or machine learning for unstructured data
  - Allowing user-defined extraction rules

---

## 💡 Best Practices

- For best results, start with well-structured, major event pages (e.g., wars, major historical events).
- Review the extracted CSV/database for completeness, especially when using less common or non-English Wikipedia pages.

---

## 🆘 Support

If you encounter issues or have suggestions for improvement, please contact the developer.

--- 