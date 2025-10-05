import { useQuery } from "@tanstack/react-query";
import { fetchProfile } from "@/lib/api";

export default function ProfilePage() {
  const { data, error, isLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: fetchProfile,
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
