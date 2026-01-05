"use client";

import { ReactNode, useEffect } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";

import { usePersistentQueryClient } from "../lib/queryClient";

type Props = {
  children: ReactNode;
};

export default function Providers({ children }: Props) {
  const { queryClient, ready } = usePersistentQueryClient();

  if (!ready) {
    return <div className="p-6 text-slate-500">Loading workspace…</div>;
  }

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
