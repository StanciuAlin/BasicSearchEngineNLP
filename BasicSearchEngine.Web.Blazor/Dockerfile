# Etapa de Build
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Copiem fișierul de proiect și restaurăm dependențele
COPY ["SearchEngine.Web.csproj", "."]
RUN dotnet restore "SearchEngine.Web.csproj"

# Copiem restul fișierelor și publicăm aplicația
COPY . .
RUN dotnet publish "SearchEngine.Web.csproj" -c Release -o /app/publish

# Etapa finală (Runtime)
FROM mcr.microsoft.com/dotnet/aspnet:9.0
WORKDIR /app
ENV ASPNETCORE_URLS=http://+:80
COPY --from=build /app/publish .
EXPOSE 80
EXPOSE 443
ENTRYPOINT ["dotnet", "SearchEngine.Web.dll"]