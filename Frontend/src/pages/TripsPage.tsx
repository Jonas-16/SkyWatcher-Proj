import { useQuery } from "@tanstack/react-query";
import { fetchTrips } from "@/lib/api";

export default function TripsPage() {
  const { data, error, isLoading } = useQuery({
    queryKey: ["trips"],
    queryFn: fetchTrips,
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading trips</div>;

  return (
    <div>
      <h1>Trips</h1>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
