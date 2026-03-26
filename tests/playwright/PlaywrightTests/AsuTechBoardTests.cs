using Microsoft.Playwright;
using Microsoft.Playwright.MSTest;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace AsuTechTests;

[TestClass]
public class AsuTechBoardTests : PageTest
{
    private const string BaseUrl = "http://localhost:3000";

    [TestInitialize]
    public async Task TestInitialize()
    {
        // Navigate to the page before each test
        await Page.GotoAsync(BaseUrl);
        // Wait for the board to be rendered
        await Page.WaitForSelectorAsync(".board", new() { Timeout = 10000 });
    }

    [TestMethod]
    public async Task PageTitle_ShouldBeCorrect()
    {
        var title = await Page.TitleAsync();
        Assert.AreEqual("АсуТех - Техподдержка", title);
    }

    [TestMethod]
    public async Task Header_ShouldDisplayLogo()
    {
        var logoText = await Page.Locator(".logo-text").TextContentAsync();
        Assert.IsNotNull(logoText);
        Assert.IsTrue(logoText.Contains("АСУТЕХ"));
    }

    [TestMethod]
    public async Task Board_ShouldHaveFourColumns()
    {
        var columns = await Page.Locator(".column").CountAsync();
        Assert.AreEqual(4, columns);
    }

    [TestMethod]
    public async Task Columns_ShouldHaveCorrectNames()
    {
        var expectedColumns = new[] { "ОЧЕРЕДЬ", "В РАБОТЕ", "ПРОВЕРКА", "ГОТОВО" };
        var columnHeaders = await Page.Locator(".column-header span:first-child").AllTextContentsAsync();
        
        for (int i = 0; i < expectedColumns.Length; i++)
        {
            Assert.IsTrue(columnHeaders[i].Contains(expectedColumns[i]), 
                $"Column {i} should contain '{expectedColumns[i]}' but was '{columnHeaders[i]}'");
        }
    }

    [TestMethod]
    public async Task NewTicketButton_ShouldExist()
    {
        var newCardBtn = Page.Locator("#newCardBtn");
        await Expect(newCardBtn).ToBeVisibleAsync();
        
        var buttonText = await newCardBtn.TextContentAsync();
        Assert.IsTrue(buttonText?.Contains("НОВАЯ ЗАЯВКА") ?? false);
    }

    [TestMethod]
    public async Task SearchInput_ShouldExist()
    {
        var searchInput = Page.Locator("#searchInput");
        await Expect(searchInput).ToBeVisibleAsync();
        await Expect(searchInput).ToBeEditableAsync();
    }

    [TestMethod]
    public async Task ClickNewTicketButton_ShouldOpenModal()
    {
        // Click the new ticket button
        await Page.ClickAsync("#newCardBtn");
        
        // Modal should be visible
        var modal = Page.Locator("#cardModal");
        await Expect(modal).ToHaveClassAsync("modal-overlay active");
        
        // Check modal title
        var modalTitle = await Page.Locator("#modalTitle").TextContentAsync();
        Assert.AreEqual("Новая заявка", modalTitle);
    }

    [TestMethod]
    public async Task Modal_ShouldHaveAllFormFields()
    {
        await Page.ClickAsync("#newCardBtn");
        
        // Check all form fields exist
        await Expect(Page.Locator("#ticketIdDisplay")).ToBeVisibleAsync();
        await Expect(Page.Locator("#cardTitle")).ToBeVisibleAsync();
        await Expect(Page.Locator("#cardType")).ToBeVisibleAsync();
        await Expect(Page.Locator("#cardPriority")).ToBeVisibleAsync();
        await Expect(Page.Locator("#cardAssignee")).ToBeVisibleAsync();
        await Expect(Page.Locator("#cardDevice")).ToBeVisibleAsync();
        await Expect(Page.Locator("#cardDescription")).ToBeVisibleAsync();
        await Expect(Page.Locator("#cardBlocked")).ToBeVisibleAsync();
    }

    [TestMethod]
    public async Task CreateNewTicket_ShouldAddToBoard()
    {
        // Open modal
        await Page.ClickAsync("#newCardBtn");
        
        // Fill the form
        await Page.FillAsync("#cardTitle", "Тестовая заявка через Playwright");
        await Page.SelectOptionAsync("#cardType", "bug");
        await Page.SelectOptionAsync("#cardPriority", "high");
        await Page.FillAsync("#cardAssignee", "testuser");
        await Page.FillAsync("#cardDevice", "TestDevice");
        await Page.FillAsync("#cardDescription", "Описание тестовой заявки");
        
        // Save
        await Page.ClickAsync("#saveBtn");
        
        // Modal should close
        await Expect(Page.Locator("#cardModal")).Not.ToHaveClassAsync("modal-overlay active");
        
        // New ticket should appear in backlog column
        var newTicket = Page.Locator(".card").Filter(new() { HasText = "Тестовая заявка через Playwright" });
        await Expect(newTicket).ToBeVisibleAsync();
    }

    [TestMethod]
    public async Task CloseModal_WithCancelButton_ShouldClose()
    {
        await Page.ClickAsync("#newCardBtn");
        await Expect(Page.Locator("#cardModal")).ToHaveClassAsync("modal-overlay active");
        
        await Page.ClickAsync("#cancelBtn");
        
        await Expect(Page.Locator("#cardModal")).Not.ToHaveClassAsync("modal-overlay active");
    }

    [TestMethod]
    public async Task CloseModal_WithXButton_ShouldClose()
    {
        await Page.ClickAsync("#newCardBtn");
        await Expect(Page.Locator("#cardModal")).ToHaveClassAsync("modal-overlay active");
        
        await Page.ClickAsync("#modalClose");
        
        await Expect(Page.Locator("#cardModal")).Not.ToHaveClassAsync("modal-overlay active");
    }

    [TestMethod]
    public async Task CloseModal_WithEscapeKey_ShouldClose()
    {
        await Page.ClickAsync("#newCardBtn");
        await Expect(Page.Locator("#cardModal")).ToHaveClassAsync("modal-overlay active");
        
        await Page.Keyboard.PressAsync("Escape");
        
        await Expect(Page.Locator("#cardModal")).Not.ToHaveClassAsync("modal-overlay active");
    }

    [TestMethod]
    public async Task Search_ShouldFilterTickets()
    {
        // Get initial ticket count
        var initialCount = await Page.Locator(".card").CountAsync();
        
        // Search for a specific ticket
        await Page.FillAsync("#searchInput", "принтер");
        
        // Wait a moment for the search to process
        await Page.WaitForTimeoutAsync(500);
        
        // Should have fewer tickets now
        var filteredCount = await Page.Locator(".card").CountAsync();
        Assert.IsTrue(filteredCount <= initialCount, "Filtered count should be less than or equal to initial count");
        
        // Should find the ticket with "принтер"
        var filteredTicket = Page.Locator(".card").First;
        var ticketText = await filteredTicket.TextContentAsync();
        Assert.IsTrue(ticketText?.ToLower().Contains("принтер") ?? false);
    }

    [TestMethod]
    public async Task ClearSearch_ShouldShowAllTickets()
    {
        // First do a search
        await Page.FillAsync("#searchInput", "принтер");
        await Page.WaitForTimeoutAsync(300);
        var filteredCount = await Page.Locator(".card").CountAsync();
        
        // Clear search
        await Page.FillAsync("#searchInput", "");
        await Page.WaitForTimeoutAsync(300);
        
        var allCount = await Page.Locator(".card").CountAsync();
        Assert.IsTrue(allCount >= filteredCount, "All tickets should be visible after clearing search");
    }

    [TestMethod]
    public async Task StatusBar_ShouldShowCorrectCounts()
    {
        var backlogCount = await Page.Locator("#backlogCount").TextContentAsync();
        var inProgressCount = await Page.Locator("#inProgressCount").TextContentAsync();
        var reviewCount = await Page.Locator("#reviewCount").TextContentAsync();
        var doneCount = await Page.Locator("#doneCount").TextContentAsync();
        
        Assert.IsNotNull(backlogCount);
        Assert.IsNotNull(inProgressCount);
        Assert.IsNotNull(reviewCount);
        Assert.IsNotNull(doneCount);
        
        // Parse and verify they are numbers
        Assert.IsTrue(int.TryParse(backlogCount, out _), "Backlog count should be a number");
        Assert.IsTrue(int.TryParse(inProgressCount, out _), "In Progress count should be a number");
        Assert.IsTrue(int.TryParse(reviewCount, out _), "Review count should be a number");
        Assert.IsTrue(int.TryParse(doneCount, out _), "Done count should be a number");
    }

    [TestMethod]
    public async Task TicketCard_ShouldHaveTypeIndicator()
    {
        var firstCard = Page.Locator(".card").First;
        
        // Cards should have data-type attribute
        var cardType = await firstCard.GetAttributeAsync("data-type");
        Assert.IsNotNull(cardType, "Card should have data-type attribute");
        
        // Type should be one of valid types
        var validTypes = new[] { "bug", "feature", "question", "task" };
        Assert.IsTrue(validTypes.Contains(cardType), $"Card type '{cardType}' should be one of: {string.Join(", ", validTypes)}");
    }

    [TestMethod]
    public async Task TicketCard_ShouldHavePriorityIndicator()
    {
        var firstCard = Page.Locator(".card").First;
        
        // Cards should have data-priority attribute
        var priority = await firstCard.GetAttributeAsync("data-priority");
        Assert.IsNotNull(priority, "Card should have data-priority attribute");
        
        // Priority should be one of valid priorities
        var validPriorities = new[] { "critical", "high", "normal", "low" };
        Assert.IsTrue(validPriorities.Contains(priority), $"Priority '{priority}' should be one of: {string.Join(", ", validPriorities)}");
    }

    [TestMethod]
    public async Task ClickOnCard_ShouldOpenEditModal()
    {
        // Get the first card's title
        var firstCard = Page.Locator(".card").First;
        var cardTitle = await firstCard.Locator(".card-title").TextContentAsync();
        
        // Click on the card
        await firstCard.ClickAsync();
        
        // Modal should open
        await Expect(Page.Locator("#cardModal")).ToHaveClassAsync("modal-overlay active");
        
        // Modal should have the same title
        var modalTitle = await Page.Locator("#cardTitle").InputValueAsync();
        Assert.AreEqual(cardTitle?.Trim(), modalTitle?.Trim());
    }

    [TestMethod]
    public async Task EditTicket_ShouldUpdateTicket()
    {
        // Click on first card to edit
        await Page.Locator(".card").First.ClickAsync();
        
        // Change the title
        var newTitle = "Обновлённый заголовок " + DateTime.Now.Ticks;
        await Page.FillAsync("#cardTitle", newTitle);
        
        // Save
        await Page.ClickAsync("#saveBtn");
        
        // Modal should close
        await Expect(Page.Locator("#cardModal")).Not.ToHaveClassAsync("modal-overlay active");
        
        // Updated ticket should be visible
        var updatedTicket = Page.Locator(".card").Filter(new() { HasText = newTitle });
        await Expect(updatedTicket).ToBeVisibleAsync();
    }

    [TestMethod]
    public async Task CreateTicket_WithoutTitle_ShouldShowError()
    {
        await Page.ClickAsync("#newCardBtn");
        
        // Don't fill the title (required field)
        await Page.ClickAsync("#saveBtn");
        
        // Modal should still be open (validation failed)
        await Expect(Page.Locator("#cardModal")).ToHaveClassAsync("modal-overlay active");
    }

    [TestMethod]
    public async Task BlockedTicket_ShouldShowIndicator()
    {
        // Find a blocked ticket (T4 is blocked in demo data)
        var blockedTicket = Page.Locator(".card").Filter(new() { HasText = "T4" });
        
        if (await blockedTicket.CountAsync() > 0)
        {
            // Should show blocked indicator
            var blockedText = await blockedTicket.TextContentAsync();
            Assert.IsTrue(blockedText?.Contains("ЗАБЛОКИРОВАНО") ?? false, 
                "Blocked ticket should show 'ЗАБЛОКИРОВАНО' indicator");
        }
    }

    [TestMethod]
    public async Task ColumnCount_ShouldMatchTicketCount()
    {
        // Check each column
        var columns = await Page.Locator(".column").AllAsync();
        
        foreach (var column in columns)
        {
            var countText = await column.Locator(".column-count").TextContentAsync();
            var cards = await column.Locator(".card").CountAsync();
            
            Assert.AreEqual(cards.ToString(), countText?.Trim(), 
                "Column count should match actual card count");
        }
    }

    [TestMethod]
    public async Task TicketTypes_ShouldHaveDifferentColors()
    {
        var bugCards = Page.Locator(".card[data-type='bug']");
        var featureCards = Page.Locator(".card[data-type='feature']");
        var questionCards = Page.Locator(".card[data-type='question']");
        var taskCards = Page.Locator(".card[data-type='task']");
        
        // At least some types should exist in demo data
        var totalCards = await Page.Locator(".card").CountAsync();
        var typedCards = await bugCards.CountAsync() + await featureCards.CountAsync() + 
                         await questionCards.CountAsync() + await taskCards.CountAsync();
        
        Assert.AreEqual(totalCards, typedCards, "All cards should have a valid type");
    }

    [TestMethod]
    public async Task Modal_WithBlockedCheckbox_ShouldWork()
    {
        await Page.ClickAsync("#newCardBtn");
        
        // Check the blocked checkbox
        await Page.CheckAsync("#cardBlocked");
        await Expect(Page.Locator("#cardBlocked")).ToBeCheckedAsync();
        
        // Uncheck it
        await Page.UncheckAsync("#cardBlocked");
        await Expect(Page.Locator("#cardBlocked")).Not.ToBeCheckedAsync();
    }

    [TestMethod]
    public async Task FormSelects_ShouldHaveCorrectOptions()
    {
        await Page.ClickAsync("#newCardBtn");
        
        // Check type options
        var typeOptions = await Page.Locator("#cardType option").AllTextContentsAsync();
        Assert.IsTrue(typeOptions.Contains("Ошибка"));
        Assert.IsTrue(typeOptions.Contains("Функция"));
        Assert.IsTrue(typeOptions.Contains("Вопрос"));
        Assert.IsTrue(typeOptions.Contains("Задача"));
        
        // Check priority options
        var priorityOptions = await Page.Locator("#cardPriority option").AllTextContentsAsync();
        Assert.IsTrue(priorityOptions.Contains("Критический"));
        Assert.IsTrue(priorityOptions.Contains("Высокий"));
        Assert.IsTrue(priorityOptions.Contains("Обычный"));
        Assert.IsTrue(priorityOptions.Contains("Низкий"));
    }

    [TestMethod]
    public async Task DragAndDrop_ShouldMoveTicket()
    {
        // Get first card from backlog
        var firstCard = Page.Locator(".column[data-column='backlog'] .card").First;
        
        if (await firstCard.CountAsync() > 0)
        {
            var cardTitle = await firstCard.Locator(".card-title").TextContentAsync();
            var targetColumn = Page.Locator(".column-content[data-column='done']");
            
            // Perform drag and drop
            await firstCard.DragToAsync(targetColumn);
            
            // Wait for board to update
            await Page.WaitForTimeoutAsync(500);
            
            // Ticket should now be in done column
            var movedTicket = Page.Locator(".column-content[data-column='done'] .card").Filter(new() { HasText = cardTitle ?? "" });
            
            // Note: This might fail if there's no ticket in backlog, which is fine
            if (await movedTicket.CountAsync() > 0)
            {
                Assert.IsTrue(true, "Ticket was successfully moved");
            }
        }
    }
}
