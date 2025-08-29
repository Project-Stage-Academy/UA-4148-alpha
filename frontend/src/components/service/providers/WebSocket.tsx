import { useAuthContext } from "@/hooks/useAuthContext";
import {
  createContext,
  useEffect,
  useRef,
  type PropsWithChildren,
  type RefObject,
} from "react";

const WebSocketContext = createContext<RefObject<WebSocket | null>>({
  current: null,
});

export const WebSocketProvider = ({ children }: PropsWithChildren) => {
  const { user, accessToken } = useAuthContext();
  const socketRef = useRef<null | WebSocket>(null);

  useEffect(() => {
    if (!accessToken || !user) return;

    // TODO: remove user_id and provide JWT
    const ws = new WebSocket(`${import.meta.env.VITE_NOTIFICATION_SERVICE}/${user?.id}`);
    socketRef.current = ws;

    socketRef.current.onopen = () => console.log("Connected");
    socketRef.current.onclose = () => console.log("Disconnected");

    return () => socketRef.current?.close();
  }, [accessToken, user]);

  useEffect(() => {
    if (!socketRef.current) return;

    socketRef.current.onmessage = (e) => {
      const message = JSON.parse(e.data);
      console.log("e", message);
    };
  }, []);

  return (
    <WebSocketContext.Provider value={socketRef}>
      {children}
    </WebSocketContext.Provider>
  );
};
