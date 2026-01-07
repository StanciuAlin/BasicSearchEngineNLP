# Build step
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Copy project file and remake the dependencies
COPY ["SearchEngine.Web.csproj", "."]
RUN dotnet restore "SearchEngine.Web.csproj"

# Copy the remaining files and publish the application
COPY . .
RUN dotnet publish "SearchEngine.Web.csproj" -c Release -o /app/publish

# Final step (Runtime)
FROM mcr.microsoft.com/dotnet/aspnet:9.0
WORKDIR /app
ENV ASPNETCORE_URLS=http://+:80
COPY --from=build /app/publish .
EXPOSE 80
EXPOSE 443
ENTRYPOINT ["dotnet", "SearchEngine.Web.dll"]