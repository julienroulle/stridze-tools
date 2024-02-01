// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.

Deno.serve(async (req) => {
  if (req.method == "POST") {
    const data = await req.json();
    console.log("webhook event received!", data);
    return new Response(JSON.stringify(data), {
      headers: { "Content-Type": "application/json" },
      status: 200,
    });
  }

  // Adds support for GET requests to our webhook
  if (req.method == "GET") {
    // Your verify token. Should be a random string.
    const VERIFY_TOKEN = "STRAVA";
    // Parses the query params
    const params = new URLSearchParams(req.url.split("?")[1]);
    let mode = params.get("hub.mode");
    let token = params.get("hub.verify_token");
    let challenge = params.get("hub.challenge");

    if (mode && token) {
      // Verifies that the mode and token sent are valid
      if (mode === "subscribe" && token === VERIFY_TOKEN) {
        // Responds with the challenge token from the request
        return new Response(JSON.stringify({ "hub.challenge": challenge }), {
          headers: { "Content-Type": "application/json" },
          status: 200,
        });
      } else {
        // Responds with '403 Forbidden' if verify tokens do not match
      }
    }
    return new Response(JSON.stringify({}), {
      headers: { "Content-Type": "application/json" },
      status: 200,
    });
  }
});

/* To invoke locally:

  1. Run `supabase start` (see: https://supabase.com/docs/reference/cli/supabase-start)
  2. Make an HTTP request:

  curl -i --location --request POST 'http://127.0.0.1:54321/functions/v1/hello-world' \
    --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0' \
    --header 'Content-Type: application/json' \
    --data '{"name":"Functions"}'

*/
