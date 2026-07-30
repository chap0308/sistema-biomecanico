"use client";

import {
  createContext,
  useContext,
  useMemo,
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
  const value = useMemo(
    () => ({ comparison, updateComparison: setComparison }),
    [comparison],
  );

  return (
    <ReferenceReviewContext value={value}>
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
