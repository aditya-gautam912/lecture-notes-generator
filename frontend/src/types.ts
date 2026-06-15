export interface QuizItem {
  question: string;
  options: string[];
  answer: string;
}

export interface StudyMaterials {
  summary: string;
  notes: string[];
  quiz: QuizItem[];
}

export interface StudyData {
  id?: number;
  filename?: string;
  transcript: string;
  materials: StudyMaterials;
  date?: string;
}

export interface HistoryItem {
  id: number;
  filename: string;
  date: string;
}
