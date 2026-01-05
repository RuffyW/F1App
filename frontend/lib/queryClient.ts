import { useEffect, useMemo, useState } from "react";
import {
  QueryClient,
  defaultShouldDehydrateQuery,
} from "@tanstack/react-query";
import { persistQueryClient } from "@tanstack/react-query-persist-client";
import { del, get, set } from "idb-keyval";

const MAX_AGE = 1000 * 60 * 60 * 24 * 7; // 7 days

function createClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 30,
        gcTime: MAX_AGE,
        refetchOnWindowFocus: true,
        refetchOnReconnect: true,
        retry: 1,
      },
      dehydrate: {
        shouldDehydrateQuery: defaultShouldDehydrateQuery,
      },
    },
  });
}

export function usePersistentQueryClient() {
  const [ready, setReady] = useState(false);
  const queryClient = useMemo(() => createClient(), []);

  useEffect(() => {
    const persister = {
      persistClient: async (client: unknown) =>
        set("f1app-query-cache", client),
      restoreClient: async () => get("f1app-query-cache"),
      removeClient: async () => del("f1app-query-cache"),
    };

    persistQueryClient({
      queryClient,
      persister,
      maxAge: MAX_AGE,
    }).finally(() => setReady(true));
  }, [queryClient]);

  return { queryClient, ready };
}
