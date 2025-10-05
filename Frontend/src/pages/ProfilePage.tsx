import { useQuery } from "@tanstack/react-query";
import api from "@/api/api";

export default function ProfilePage() {
  const { data, error, isLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: api.getProfile,
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading profile</div>;

  return (
    <div>
      <h1>Profile</h1>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
