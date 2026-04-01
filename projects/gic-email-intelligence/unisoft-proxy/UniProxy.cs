using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Text;
using System.Threading;

class UniProxy
{
    static string apiKey;
    static DateTime startTime;
    static int requestCount = 0;
    static DateTime lastRequestTime;
    static long maxRequestBytes;

    static void Main(string[] args)
    {
        apiKey = Environment.GetEnvironmentVariable("PROXY_API_KEY") ?? "dev-key";
        int port = int.Parse(Environment.GetEnvironmentVariable("PROXY_PORT") ?? "5000");
        maxRequestBytes = long.Parse(
            Environment.GetEnvironmentVariable("PROXY_MAX_REQUEST_BYTES") ?? "5242880");
        startTime = DateTime.UtcNow;

        HttpListener listener = new HttpListener();
        listener.Prefixes.Add(string.Format("http://+:{0}/", port));
        listener.Start();
        Console.WriteLine("UniProxy v0.2 listening on port " + port);

        while (true)
        {
            HttpListenerContext ctx = listener.GetContext();
            ThreadPool.QueueUserWorkItem(delegate { HandleRequest(ctx); });
        }
    }

    static void HandleRequest(HttpListenerContext ctx)
    {
        try
        {
            string path = ctx.Request.Url.AbsolutePath.ToLower();
            string rawPath = ctx.Request.Url.AbsolutePath;

            // Health check — no auth required
            if (path == "/api/health")
            {
                string lastReq = lastRequestTime > DateTime.MinValue
                    ? "\"" + lastRequestTime.ToString("o") + "\"" : "null";
                string json = "{\"status\":\"ok\",\"uptime_seconds\":" +
                    (int)(DateTime.UtcNow - startTime).TotalSeconds +
                    ",\"requests\":" + requestCount +
                    ",\"channel_state\":\"not_started\"" +
                    ",\"last_request_time\":" + lastReq + "}";
                WriteJson(ctx, 200, json);
                return;
            }

            // Meta — no auth required
            if (path == "/api/meta/operations")
            {
                WriteJson(ctx, 200,
                    "{\"service\":\"IIMSService\",\"operations\":910," +
                    "\"usage\":\"POST /api/soap/{OperationName} with JSON body\"," +
                    "\"wsdl\":\"https://services.uat.gicunderwriters.co/management/imsservice.svc?singleWsdl\"}");
                return;
            }

            // API key check for all other endpoints
            string key = ctx.Request.Headers["X-Api-Key"];
            if (key != apiKey)
            {
                WriteJson(ctx, 401, "{\"error\":\"unauthorized\"}");
                return;
            }

            // SOAP passthrough
            if (path.StartsWith("/api/soap/") && ctx.Request.HttpMethod == "POST")
            {
                if (ctx.Request.ContentLength64 > maxRequestBytes)
                {
                    WriteJson(ctx, 413,
                        "{\"error\":\"request_too_large\",\"max_bytes\":" + maxRequestBytes + "}");
                    return;
                }

                string opName = rawPath.Substring("/api/soap/".Length);
                Interlocked.Increment(ref requestCount);
                lastRequestTime = DateTime.UtcNow;

                // TODO: wire to SOAP bridge (Task A3)
                WriteJson(ctx, 501,
                    "{\"error\":\"not_implemented\",\"operation\":\"" + opName + "\"}");
                return;
            }

            WriteJson(ctx, 404, "{\"error\":\"not_found\"}");
        }
        catch (Exception ex)
        {
            try
            {
                WriteJson(ctx, 500,
                    "{\"error\":\"proxy_error\",\"message\":\"" +
                    ex.Message.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"}");
            }
            catch { }
        }
    }

    static void WriteJson(HttpListenerContext ctx, int status, string json)
    {
        byte[] buf = Encoding.UTF8.GetBytes(json);
        ctx.Response.StatusCode = status;
        ctx.Response.ContentType = "application/json";
        ctx.Response.ContentLength64 = buf.Length;
        ctx.Response.OutputStream.Write(buf, 0, buf.Length);
        ctx.Response.Close();
    }
}
