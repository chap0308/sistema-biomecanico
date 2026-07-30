"use client";

import {
  createContext,
  useContext,
  useState,
  type ReactNode,
} from "react";

import type { CaseComparison } from "@/types/squat-comparison";

type ReferenceReviewContextValue = {
  comparison: CaseComparison;
  updateComparison: (comparison: CaseComparison) => void;
};

const ReferenceReviewContext =
  createContext<ReferenceReviewContextValue | null>(null);

export function ReferenceReviewProvider({
  initialComparison,
  children,
}: {
  initialComparison: CaseComparison;
  children: ReactNode;
}) {
  const [comparison, setComparison] = useState(initialComparison);

  return (
    <ReferenceReviewContext
      value={{ comparison, updateComparison: setComparison }}
    >
      {children}
    </ReferenceReviewContext>
  );
}

export function useReferenceReview() {
  const context = useContext(ReferenceReviewContext);
  if (!context) {
    throw new Error(
      "useReferenceReview must be used within ReferenceReviewProvider.",
    );
  }
  return context;
}
